"""
User Models

Defines user-related Pydantic models for authentication and user management.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import re


class UserRole(str, Enum):
    """User roles for access control"""
    STUDENT = "student"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.lower()


class UserCreate(UserBase):
    """Model for user registration"""
    password: str = Field(..., min_length=8)
    confirm_password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        # Relaxed validation for better user experience
        # Password just needs to be at least 8 characters
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
    
    def validate_passwords_match(self) -> bool:
        return self.password == self.confirm_password


class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Model for user response (excludes sensitive data)"""
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.STUDENT
    created_at: datetime
    is_active: bool = True
    current_track: Optional[str] = None
    streak_days: int = 0
    total_problems_solved: int = 0
    
    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """Model for user stored in database"""
    id: Optional[str] = Field(None, alias="_id")
    hashed_password: str
    role: UserRole = UserRole.STUDENT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    is_verified: bool = False
    
    # Learning progress
    current_track: Optional[str] = None  # java_dsa, data_science, ai_engineer
    streak_days: int = 0
    last_activity_date: Optional[datetime] = None
    total_problems_solved: int = 0
    
    class Config:
        populate_by_name = True


class User(UserBase):
    """Full user model"""
    id: str
    role: UserRole = UserRole.STUDENT
    created_at: datetime
    is_active: bool = True
    current_track: Optional[str] = None
    streak_days: int = 0
    total_problems_solved: int = 0


class TokenData(BaseModel):
    """JWT Token payload data"""
    user_id: str
    email: EmailStr
    role: UserRole
    exp: Optional[datetime] = None


class TokenResponse(BaseModel):
    """Response model for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
