import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from jose import JWTError, jwt
from dotenv import load_dotenv
import secrets
import bcrypt

import models, schemas, database, ntfy_client


load_dotenv()

# Environment variables generation
env_path = os.path.join(os.path.dirname(__file__), ".env")
env_updates = []

# generate a random secret token for ESP32 if not set, and save to /api/.env
ESP32_SECRET_TOKEN = os.getenv("ESP32_SECRET_TOKEN")
if not ESP32_SECRET_TOKEN:
    ESP32_SECRET_TOKEN = secrets.token_hex(16)
    os.environ["ESP32_SECRET_TOKEN"] = ESP32_SECRET_TOKEN
    env_updates.append(f"ESP32_SECRET_TOKEN={ESP32_SECRET_TOKEN}")
    print(f"Generated ESP32_SECRET_TOKEN: {ESP32_SECRET_TOKEN}")

NTFY_SYSTEM_USER = os.getenv("NTFY_SYSTEM_USER", "system_backend")
os.environ["NTFY_SYSTEM_USER"] = NTFY_SYSTEM_USER

# generate a random password for ntfy system user if not set, and save to /api/.env
NTFY_SYSTEM_PASS = os.getenv("NTFY_SYSTEM_PASS")
if not NTFY_SYSTEM_PASS:
    NTFY_SYSTEM_PASS = secrets.token_hex(16)
    os.environ["NTFY_SYSTEM_PASS"] = NTFY_SYSTEM_PASS
    env_updates.append(f"NTFY_SYSTEM_USER={NTFY_SYSTEM_USER}")
    env_updates.append(f"NTFY_SYSTEM_PASS={NTFY_SYSTEM_PASS}")
    print(f"Generated NTFY_SYSTEM_PASS: {NTFY_SYSTEM_PASS}")

if env_updates:
    with open(env_path, "a") as f:
        for update in env_updates:
            f.write(f"{update}\n")
    print(f"Saved new generated tokens to {env_path}")


SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize Database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="IoT Doorbell API",
    description="API of the backend for the IoT Doorbell project. Handles authentication, event logging, and pushing notifications to ntfy.",
    version="1.0.0"
)

@app.on_event("startup")
def init_defaults():
    db = database.SessionLocal()
    try:
        if db.query(models.User).count() == 0:
            hashed = get_password_hash("admin")
            admin_user = models.User(username="admin", hashed_password=hashed, is_admin=True)
            db.add(admin_user)
            db.commit()
            print("Default admin user 'admin' created with password 'admin'")
            
            try:
                ntfy_client.ntfy_add_user("admin", "admin", role="admin")
            except Exception as e:
                print("Could not create admin user in ntfy:", e)
    except Exception as e:
        print("Error initializing defaults:", e)
    finally:
        db.close()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security schemes
esp32_auth_scheme = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login") # used by frontend to get JWT token


# --- Helper functions ---

def verify_password(plain_password, hashed_password):
    """
    Verify a plaintext password against a hashed password using bcrypt
    args:
    - plain_password [str]: the plaintext password to verify
    - hashed_password [str]: the bcrypt hashed password to compare against
    """
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def get_password_hash(password):
    """
    Hash a plaintext password using bcrypt
    args:
    - password [str]: the plaintext password to hash
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a JWT access token
    args:
    - data [dict]: the data to include in the token payload (e.g. {"sub": "user_id"})
    - expires_delta [timedelta | None]: the time delta after which the token will expire
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Decode the JWT token to get the current user. Raises HTTP 401 if token is invalid or user doesn't exist.
    args:
    - token [str]: the JWT token from the Authorization header
    - db [Session]: the database session for querying the user
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def verify_esp32_token(credentials: HTTPAuthorizationCredentials = Depends(esp32_auth_scheme)):
    """
    Verify the token sent by the ESP32 in the Authorization header. Raises HTTP 401 if token is invalid.
    args:
    - credentials [HTTPAuthorizationCredentials]: the credentials object from the HTTPBearer dependency, containing the token sent by the ESP32
    """
    if credentials.credentials != ESP32_SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ESP32 Token",
        )
    return True

# --- API Routes ---
@app.get("/")
def read_root():
    """
    Simple root endpoint to check if API is running
    """
    return {"message": "IoT Doorbell Backend is running"}

# --- ESP32 Route ---
@app.post("/api/events", status_code=status.HTTP_201_CREATED)
def receive_event(event: schemas.EventCreate, db: Session = Depends(database.get_db), authorized: bool = Depends(verify_esp32_token)):
    """
    Endpoint for ESP32 to send events (doorbell press, motion detected). Logs the event to the database and pushes a notification to ntfy.
    args:
    - event [schemas.EventCreate]: the event data sent by the ESP32, containing at least the event_type (e.g. "button" or "motion")
    - db [Session]: the database session for logging the event
    - authorized [bool]: the authorization status for the ESP32 token
    """
    
    # 1. Log to database
    db_event = models.EventLog(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    # 2. Push to Ntfy
    ts = db_event.timestamp
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    local_ts = ts.astimezone(ZoneInfo("America/Montreal"))
    
    # create a notification title and message based on the event type
    assert event.event_type in ['button', 'motion'], "Invalid event type"
    title = "Doorbell Alert!" if event.event_type == 'button' else "Motion Detected"
    message = f"Event type: {event.event_type} at {local_ts.strftime('%Y-%m-%d %H:%M:%S')}"
    tags = ["bell"] if event.event_type == 'button' else ["eyes"] # tag to display emoji icon in ntfy
    ntfy_client.push_notification(title, message, tags)
    
    return {"status": "success", "event_id": db_event.id}

# --- Auth Routes ---
@app.post("/api/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """
    Authenticate a user and return an access token.
    args:
    - form_data [OAuth2PasswordRequestForm]: the form data containing the username and password
    - db [Session]: the database session for querying users
    """

    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Frontend Routes (Protected) ---
@app.get("/api/logs", response_model=list[schemas.EventLog])
def get_logs(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    Get a list of event logs, protected by JWT authentication. Only accessible to authenticated users.
    args:
    - skip [int]: the number of records to skip for pagination
    - limit [int]: the maximum number of records to return
    - db [Session]: the database session for querying event logs
    - current_user [models.User]: the currently authenticated user, obtained from the JWT token"""
    
    logs = db.query(models.EventLog).order_by(models.EventLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

@app.get("/api/users", response_model=list[schemas.User])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    List all users, protected by JWT authentication. Only accessible to admin users.
    args:
    - skip [int]: the number of records to skip for pagination
    - limit [int]: the maximum number of records to return
    - db [Session]: the database session for querying users
    - current_user [models.User]: the currently authenticated user, obtained from the JWT token
    """
    
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can list users")
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.post("/api/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    Create a new user, protected by JWT authentication. Only accessible to admin users. Also creates the user in ntfy with the same password.
    args:
    - user [schemas.UserCreate]: the user data for the new user, containing at least the username and password
    - db [Session]: the database session for creating the user
    - current_user [models.User]: the currently authenticated user, obtained from the JWT token
    """
    
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can create users")
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create in DB
    hashed_password = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password, is_admin=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create in Ntfy (role="user")
    success = ntfy_client.ntfy_add_user(user.username, user.password, role="user")
    if not success:
        pass
        
    return new_user

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    Delete a user, protected by JWT authentication. Only accessible to admin users.
    args:
    - user_id [int]: the ID of the user to delete
    - db [Session]: the database session for querying users
    - current_user [models.User]: the currently authenticated user, obtained from the JWT token
    """
    
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can delete users")
        
    user_to_delete = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user_to_delete.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own admin account")
        
    db.delete(user_to_delete)
    db.commit()
    
    ntfy_client.ntfy_delete_user(user_to_delete.username)
    return {"status": "success"}

@app.put("/api/users/{user_id}/password")
def update_password(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    Update a user's password, protected by JWT authentication. Only accessible to the user themselves or admin users.
    args:
    - user_id [int]: the ID of the user whose password to update
    - user_update [schemas.UserUpdate]: the new password for the user
    - db [Session]: the database session for querying users
    - current_user [models.User]: the currently authenticated user, obtained from the JWT token
    """

    # Allow user to change their own password, or admin (omitted for simplicity, assume current_user == user_id)
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to change this user's password")
        
    hashed_password = get_password_hash(user_update.password)
    current_user.hashed_password = hashed_password
    db.commit()
    
    # Update in Ntfy
    ntfy_client.ntfy_change_password(current_user.username, user_update.password)
    
    return {"status": "password updated"}

@app.get("/api/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Get the current authenticated user's information.
    args:
    - current_user [models.User]: the currently authenticated user, obtained from the JWT token
    """
    return current_user
