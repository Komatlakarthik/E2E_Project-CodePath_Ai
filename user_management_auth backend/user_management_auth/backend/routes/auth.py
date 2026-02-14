"""
Authentication Routes

Handles user registration, login, and token management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional

from models.user import UserCreate, UserLogin, UserResponse, TokenData, UserRole
from services.auth_service import AuthService
from utils.security import get_current_user

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user account.
    
    - Validates email and username uniqueness
    - Hashes password securely
    - Creates user with 'student' role by default
    """
    # Validate passwords match
    if not user_data.validate_passwords_match():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    auth_service = AuthService()
    result = await auth_service.register_user(user_data)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {
        "message": "User registered successfully",
        "user": result["user"]
    }


@router.post("/login", response_model=dict)
async def login_user(credentials: UserLogin):
    """
    Authenticate user and return JWT tokens.
    
    Returns:
    - access_token: Short-lived token for API access
    - refresh_token: Long-lived token for refreshing access
    """
    auth_service = AuthService()
    result = await auth_service.authenticate_user(
        credentials.email,
        credentials.password
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["error"],
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {
        "message": "Login successful",
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type": "bearer",
        "expires_in": result["expires_in"],
        "user": result["user"]
    }


@router.post("/refresh", response_model=dict)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh access token using refresh token.
    """
    auth_service = AuthService()
    result = await auth_service.refresh_access_token(credentials.credentials)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["error"],
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {
        "access_token": result["access_token"],
        "token_type": "bearer",
        "expires_in": result["expires_in"]
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current authenticated user's information.
    """
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        username=current_user["username"],
        full_name=current_user.get("full_name"),
        role=current_user.get("role", UserRole.STUDENT),
        created_at=current_user["created_at"],
        is_active=current_user.get("is_active", True),
        current_track=current_user.get("current_track"),
        streak_days=current_user.get("streak_days", 0),
        total_problems_solved=current_user.get("total_problems_solved", 0)
    )


@router.post("/logout", response_model=dict)
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict = Depends(get_current_user)
):
    """
    Logout user and invalidate tokens.
    """
    auth_service = AuthService()
    await auth_service.logout_user(
        str(current_user["_id"]),
        credentials.credentials
    )
    
    return {"message": "Logged out successfully"}


@router.put("/change-password", response_model=dict)
async def change_password(
    current_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user's password.
    """
    auth_service = AuthService()
    result = await auth_service.change_password(
        str(current_user["_id"]),
        current_password,
        new_password
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"message": "Password changed successfully"}


@router.put("/update-profile", response_model=UserResponse)
async def update_profile(
    full_name: Optional[str] = None,
    current_track: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user profile information.
    """
    auth_service = AuthService()
    updated_user = await auth_service.update_profile(
        str(current_user["_id"]),
        full_name=full_name,
        current_track=current_track
    )
    
    return UserResponse(
        id=str(updated_user["_id"]),
        email=updated_user["email"],
        username=updated_user["username"],
        full_name=updated_user.get("full_name"),
        role=updated_user.get("role", UserRole.STUDENT),
        created_at=updated_user["created_at"],
        is_active=updated_user.get("is_active", True),
        current_track=updated_user.get("current_track"),
        streak_days=updated_user.get("streak_days", 0),
        total_problems_solved=updated_user.get("total_problems_solved", 0)
    )
