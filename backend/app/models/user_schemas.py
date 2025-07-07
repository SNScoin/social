from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserProfileUpdate(BaseModel):
    """Schema for updating user profile information"""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    
    @validator('display_name')
    def validate_display_name(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        if v is not None and len(v) > 100:
            raise ValueError('Display name must be less than 100 characters')
        return v
    
    @validator('bio')
    def validate_bio(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('Bio must be less than 500 characters')
        return v
    
    @validator('timezone')
    def validate_timezone(cls, v):
        if v is not None and v not in [
            'UTC', 'America/New_York', 'America/Chicago', 'America/Denver', 
            'America/Los_Angeles', 'Europe/London', 'Europe/Paris', 
            'Asia/Tokyo', 'Asia/Shanghai', 'Australia/Sydney'
        ]:
            raise ValueError('Invalid timezone')
        return v

class UserProfileResponse(BaseModel):
    """Schema for user profile response"""
    id: int
    username: str
    email: str
    display_name: Optional[str] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    timezone: str = "UTC"
    email_verified: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True

class PasswordChangeRequest(BaseModel):
    """Schema for password change request"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class AccountDeletionRequest(BaseModel):
    """Schema for account deletion request"""
    password: str
    confirmation: str = "DELETE"
    
    @validator('confirmation')
    def validate_confirmation(cls, v):
        if v != "DELETE":
            raise ValueError('Please type "DELETE" to confirm account deletion')
        return v

class ProfilePictureUpload(BaseModel):
    """Schema for profile picture upload response"""
    profile_picture_url: str
    message: str = "Profile picture updated successfully" 