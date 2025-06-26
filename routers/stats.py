from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.db.database import get_db
from backend.app.models.models import SocialLink, Platform
from backend.app.schemas import SocialLinkCreate, SocialLinkUpdate, SocialLink
from typing import List, Dict
from pydantic import BaseModel

router = APIRouter(prefix="/stats", tags=["stats"])

class PlatformStats(BaseModel):
    total_links: int = 0
    total_views: int = 0
    total_likes: int = 0
    total_comments: int = 0

class StatsResponse(BaseModel):
    total_links: int = 0
    processed_links: int = 0
    total_views: int = 0
    total_likes: int = 0
    total_comments: int = 0
    platform_stats: Dict[str, PlatformStats] = {}

@router.get("/{platform}", response_model=List[SocialLink])
async def get_stats(platform: str, db: Session = Depends(get_db)):
    try:
        platform_enum = Platform[platform]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    return db.query(SocialLink).filter(SocialLink.platform == platform_enum).all()

@router.post("/{platform}", response_model=SocialLink)
async def add_link(
    platform: str,
    link: SocialLinkCreate,
    db: Session = Depends(get_db)
):
    try:
        platform_enum = Platform[platform]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    db_link = SocialLink(**link.dict())
    db_link.platform = platform_enum
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

@router.patch("/{link_id}", response_model=SocialLink)
async def update_link(
    link_id: int,
    link_update: SocialLinkUpdate,
    db: Session = Depends(get_db)
):
    db_link = db.query(SocialLink).filter(SocialLink.id == link_id).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    for field, value in link_update.dict(exclude_unset=True).items():
        setattr(db_link, field, value)
    
    db.commit()
    db.refresh(db_link)
    return db_link

@router.get("/api/stats/", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    try:
        # Initialize response
        response = StatsResponse()
        
        # Get total counts
        response.total_links = db.query(func.count(SocialLink.id)).scalar() or 0
        response.processed_links = db.query(func.count(SocialLink.id)).filter(SocialLink.is_processed == True).scalar() or 0
        
        # Get total metrics for all platforms
        metrics = db.query(
            func.sum(SocialLink.views).label('total_views'),
            func.sum(SocialLink.likes).label('total_likes'),
            func.sum(SocialLink.comments).label('total_comments')
        ).filter(SocialLink.is_processed == True).first()
        
        response.total_views = metrics.total_views or 0
        response.total_likes = metrics.total_likes or 0
        response.total_comments = metrics.total_comments or 0
        
        # Get stats per platform
        for platform in Platform:
            platform_metrics = db.query(
                func.count(SocialLink.id).label('total_links'),
                func.sum(SocialLink.views).label('total_views'),
                func.sum(SocialLink.likes).label('total_likes'),
                func.sum(SocialLink.comments).label('total_comments')
            ).filter(
                SocialLink.platform == platform,
                SocialLink.is_processed == True
            ).first()
            
            response.platform_stats[platform.value] = PlatformStats(
                total_links=db.query(func.count(SocialLink.id)).filter(SocialLink.platform == platform).scalar() or 0,
                total_views=platform_metrics.total_views or 0,
                total_likes=platform_metrics.total_likes or 0,
                total_comments=platform_metrics.total_comments or 0
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") 