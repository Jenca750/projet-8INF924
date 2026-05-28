from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

"""
This file defines the database models for the application using SQLAlchemy ORM.
- EventLog: represents an event that occurred (e.g., motion detected, button pressed)
- User: represents a user of the system with authentication credentials and admin status
"""

class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True) # e.g., 'motion', 'button'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
