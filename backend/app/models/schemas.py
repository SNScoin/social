from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from backend.app.models.models import Platform

class LinkSubmission(BaseModel):
    url: str = Field(..., description="The URL of the social media post")
    company_id: int = Field(..., description="The ID of the company this link belongs to")
    platform: Optional[str] = Field(None, description="The platform (youtube, tiktok, instagram, facebook)")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "company_id": 1,
                "platform": "youtube"
            }
        }
    )

class LinkMetricsBase(BaseModel):
    views: int = 0
    likes: int = 0
    comments: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class LinkBase(BaseModel):
    url: str
    platform: str
    title: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class LinkCreate(LinkBase):
    company_id: int
    
    model_config = ConfigDict(from_attributes=True)

class LinkResponse(LinkBase):
    id: int
    user_id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LinkMetricsResponse(LinkMetricsBase):
    id: int
    link_id: int
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LinkWithMetricsResponse(LinkResponse):
    metrics: Optional[LinkMetricsResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

class CompanyBase(BaseModel):
    name: str
    
    model_config = ConfigDict(from_attributes=True)

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: int
    owner_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    email: str
    username: str
    
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    
    model_config = ConfigDict(from_attributes=True)

class TokenData(BaseModel):
    email: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True) 