"""
Authentication Service

Handles user registration, login, token management, and password operations.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from bson import ObjectId

from config.database import get_users_collection, get_database
from config.settings import settings
from models.user import UserCreate, UserRole
from utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    validate_password_strength
)


class AuthService:
    """
    Authentication service handling all auth-related operations.
    """
    
    def __init__(self):
        self.users_collection = get_users_collection()
    
    async def register_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Dict with success status and user data or error
        """
        # Check if email already exists
        existing_email = await self.users_collection.find_one(
            {"email": user_data.email}
        )
        if existing_email:
            return {"success": False, "error": "Email already registered"}
        
        # Check if username already exists
        existing_username = await self.users_collection.find_one(
            {"username": user_data.username.lower()}
        )
        if existing_username:
            return {"success": False, "error": "Username already taken"}
        
        # Validate password strength
        is_valid, error_msg = validate_password_strength(user_data.password)
        if not is_valid:
            return {"success": False, "error": error_msg}
        
        # Create user document
        user_doc = {
            "email": user_data.email,
            "username": user_data.username.lower(),
            "full_name": user_data.full_name,
            "hashed_password": hash_password(user_data.password),
            "role": UserRole.STUDENT,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "is_verified": False,
            "current_track": None,
            "streak_days": 0,
            "last_activity_date": None,
            "total_problems_solved": 0,
            "daily_goal": 3,
            "preferences": {
                "theme": "dark",
                "editor_font_size": 14,
                "notifications_enabled": True
            }
        }
        
        # Insert into database
        result = await self.users_collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        # Return sanitized user data
        return {
            "success": True,
            "user": {
                "id": str(result.inserted_id),
                "email": user_doc["email"],
                "username": user_doc["username"],
                "full_name": user_doc["full_name"],
                "role": user_doc["role"]
            }
        }
    
    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Authenticate user and return tokens.
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Dict with tokens and user data or error
        """
        # Find user by email
        user = await self.users_collection.find_one({"email": email})
        
        if not user:
            return {"success": False, "error": "Invalid email or password"}
        
        # Verify password
        if not verify_password(password, user["hashed_password"]):
            return {"success": False, "error": "Invalid email or password"}
        
        # Check if account is active
        if not user.get("is_active", True):
            return {"success": False, "error": "Account is inactive"}
        
        # Create tokens
        token_data = {
            "sub": str(user["_id"]),
            "email": user["email"],
            "role": user["role"]
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Update last activity
        await self.users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "last_activity_date": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Update streak
        await self._update_streak(str(user["_id"]))
        
        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user["username"],
                "full_name": user.get("full_name"),
                "role": user["role"],
                "current_track": user.get("current_track"),
                "streak_days": user.get("streak_days", 0),
                "total_problems_solved": user.get("total_problems_solved", 0)
            }
        }
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Dict with new access token or error
        """
        try:
            payload = decode_token(refresh_token)
            
            # Verify it's a refresh token
            if payload.get("type") != "refresh":
                return {"success": False, "error": "Invalid token type"}
            
            user_id = payload.get("sub")
            
            # Verify user still exists and is active
            user = await self.users_collection.find_one(
                {"_id": ObjectId(user_id)}
            )
            
            if not user or not user.get("is_active", True):
                return {"success": False, "error": "User not found or inactive"}
            
            # Create new access token
            token_data = {
                "sub": str(user["_id"]),
                "email": user["email"],
                "role": user["role"]
            }
            
            new_access_token = create_access_token(token_data)
            
            return {
                "success": True,
                "access_token": new_access_token,
                "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except Exception as e:
            return {"success": False, "error": "Invalid refresh token"}
    
    async def logout_user(self, user_id: str, token: str) -> Dict[str, Any]:
        """
        Logout user (invalidate token).
        
        For a production system, you'd want to maintain a token blacklist.
        Here we just update the last logout time.
        
        Args:
            user_id: User's ID
            token: Token to invalidate
            
        Returns:
            Success status
        """
        await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_logout": datetime.utcnow()}}
        )
        
        return {"success": True}
    
    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> Dict[str, Any]:
        """
        Change user's password.
        
        Args:
            user_id: User's ID
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            Success status or error
        """
        user = await self.users_collection.find_one(
            {"_id": ObjectId(user_id)}
        )
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Verify current password
        if not verify_password(current_password, user["hashed_password"]):
            return {"success": False, "error": "Current password is incorrect"}
        
        # Validate new password
        is_valid, error_msg = validate_password_strength(new_password)
        if not is_valid:
            return {"success": False, "error": error_msg}
        
        # Update password
        await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "hashed_password": hash_password(new_password),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"success": True}
    
    async def update_profile(
        self,
        user_id: str,
        full_name: Optional[str] = None,
        current_track: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update user profile information.
        
        Args:
            user_id: User's ID
            full_name: New full name (optional)
            current_track: New current track (optional)
            
        Returns:
            Updated user document
        """
        update_data = {"updated_at": datetime.utcnow()}
        
        if full_name is not None:
            update_data["full_name"] = full_name
        
        if current_track is not None:
            # Validate track
            valid_tracks = ["java_dsa", "data_science", "ai_engineer"]
            if current_track not in valid_tracks:
                raise ValueError(f"Invalid track. Must be one of: {valid_tracks}")
            update_data["current_track"] = current_track
        
        await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        # Return updated user
        user = await self.users_collection.find_one(
            {"_id": ObjectId(user_id)}
        )
        
        return user
    
    async def _update_streak(self, user_id: str) -> None:
        """
        Update user's streak based on activity.
        
        Args:
            user_id: User's ID
        """
        user = await self.users_collection.find_one(
            {"_id": ObjectId(user_id)}
        )
        
        if not user:
            return
        
        last_activity = user.get("last_activity_date")
        current_streak = user.get("streak_days", 0)
        
        today = datetime.utcnow().date()
        
        if last_activity:
            last_activity_date = last_activity.date()
            days_diff = (today - last_activity_date).days
            
            if days_diff == 0:
                # Same day, no change
                return
            elif days_diff == 1:
                # Consecutive day, increment streak
                current_streak += 1
            else:
                # Streak broken, reset to 1
                current_streak = 1
        else:
            # First activity
            current_streak = 1
        
        await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"streak_days": current_streak}}
        )
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: User's ID
            
        Returns:
            User document or None
        """
        return await self.users_collection.find_one(
            {"_id": ObjectId(user_id)}
        )
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email.
        
        Args:
            email: User's email
            
        Returns:
            User document or None
        """
        return await self.users_collection.find_one({"email": email})
