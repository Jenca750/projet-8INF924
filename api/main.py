from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
from jose import JWTError, jwt
from dotenv import load_dotenv
import secrets

load_dotenv()

import models, schemas, database, ntfy_client

# Environment variables
ESP32_SECRET_TOKEN = os.getenv("ESP32_SECRET_TOKEN")
if not ESP32_SECRET_TOKEN:
    ESP32_SECRET_TOKEN = secrets.token_hex(16)
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    with open(env_path, "a") as f:
        f.write(f"ESP32_SECRET_TOKEN={ESP32_SECRET_TOKEN}\n")
    print(f"Generated ESP32_SECRET_TOKEN: {ESP32_SECRET_TOKEN} and saved to {env_path}")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize Database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="IoT Doorbell API")

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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

import bcrypt

# --- Helper functions ---

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def get_password_hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
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
    if credentials.credentials != ESP32_SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ESP32 Token",
        )
    return True

# --- API Routes ---

@app.get("/")
def read_root():
    return {"message": "IoT Doorbell Backend is running"}

# --- ESP32 Route ---
@app.post("/api/events", status_code=status.HTTP_201_CREATED)
def receive_event(event: schemas.EventCreate, db: Session = Depends(database.get_db), authorized: bool = Depends(verify_esp32_token)):
    # 1. Log to database
    db_event = models.EventLog(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    # 2. Push to Ntfy
    title = "Doorbell Alert!" if event.event_type == 'button' else "Motion Detected"
    message = f"Event type: {event.event_type} at {db_event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    tags = ["bell"] if event.event_type == 'button' else ["eyes"]
    ntfy_client.push_notification(title, message, tags)
    
    return {"status": "success", "event_id": db_event.id}

# --- Auth Routes ---
@app.post("/api/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
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
    logs = db.query(models.EventLog).order_by(models.EventLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

@app.get("/api/users", response_model=list[schemas.User])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can list users")
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.post("/api/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
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
    return current_user
