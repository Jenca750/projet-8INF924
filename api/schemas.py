from pydantic import BaseModel
from datetime import datetime
from typing import Optional

"""
Pydantic models for request and response validation in FastAPI.
These models define the expected structure of data for API endpoints, such as creating events, managing users, and authentication tokens.
"""

class EventCreate(BaseModel):
    event_type: str
    details: Optional[str] = None

class EventLog(EventCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    password: str

class User(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
