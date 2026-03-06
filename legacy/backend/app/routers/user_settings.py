from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import os
import shutil
from datetime import datetime
from pathlib import Path

from backend.app.db.database import get_db
from backend.app.models.models import User
from backend.app.models.user_schemas import (
    UserProfileUpdate, UserProfileResponse, PasswordChangeRequest, 
    AccountDeletionRequest, ProfilePictureUpload
)
from backend.app.core.auth import get_current_user, get_password_hash, verify_password

router = APIRouter(prefix="/api/user", tags=["user-settings"])

# Create uploads directory if it doesn't exist
UPLOADS_DIR = Path("backend/app/static/uploads/profile_pictures")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile information"""
    return UserProfileResponse.from_orm(current_user)

@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile information"""
    try:
        # Update only provided fields
        if profile_update.display_name is not None:
            current_user.display_name = profile_update.display_name
        if profile_update.bio is not None:
            current_user.bio = profile_update.bio
        if profile_update.timezone is not None:
            current_user.timezone = profile_update.timezone
        
        db.commit()
        db.refresh(current_user)
        
        return current_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.post("/profile/picture", response_model=ProfilePictureUpload)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile picture"""
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Validate file size (max 5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    try:
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if file.filename else 'jpg'
        filename = f"profile_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        file_path = UPLOADS_DIR / filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update user profile picture URL
        profile_picture_url = f"/static/uploads/profile_pictures/{filename}"
        current_user.profile_picture = profile_picture_url
        
        db.commit()
        
        return ProfilePictureUpload(profile_picture_url=profile_picture_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload profile picture: {str(e)}"
        )

@router.post("/change-password")
async def change_password(
    password_request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not verify_password(password_request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Check if new password is different from current
    if verify_password(password_request.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    try:
        # Update password
        current_user.hashed_password = get_password_hash(password_request.new_password)
        db.commit()
        
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )

@router.delete("/account")
async def delete_account(
    deletion_request: AccountDeletionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account"""
    # Verify password
    if not verify_password(deletion_request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect"
        )
    
    try:
        # Delete profile picture if exists
        if current_user.profile_picture:
            try:
                picture_path = Path("backend/app") / current_user.profile_picture.lstrip('/')
                if picture_path.exists():
                    picture_path.unlink()
            except Exception:
                pass  # Ignore errors when deleting profile picture
        
        # Delete user (this will cascade to related data)
        db.delete(current_user)
        db.commit()
        
        return {"message": "Account deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )

@router.get("/timezones")
async def get_available_timezones():
    """Get list of available timezones"""
    return {
        "timezones": [
            {"value": "UTC", "label": "UTC (Coordinated Universal Time)"},
            {"value": "America/New_York", "label": "Eastern Time (ET)"},
            {"value": "America/Chicago", "label": "Central Time (CT)"},
            {"value": "America/Denver", "label": "Mountain Time (MT)"},
            {"value": "America/Los_Angeles", "label": "Pacific Time (PT)"},
            {"value": "Europe/London", "label": "London (GMT/BST)"},
            {"value": "Europe/Paris", "label": "Paris (CET/CEST)"},
            {"value": "Asia/Tokyo", "label": "Tokyo (JST)"},
            {"value": "Asia/Shanghai", "label": "Shanghai (CST)"},
            {"value": "Australia/Sydney", "label": "Sydney (AEST/AEDT)"}
        ]
    } 