from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from backend.app.db.database import get_db
from backend.app.models.models import SocialLink
from pydantic import BaseModel
from backend.app.parsers.parser_factory import ParserFactory

router = APIRouter()
parser_factory = ParserFactory()

class LinkCreate(BaseModel):
    url: str

class LinkResponse(BaseModel):
    id: int
    url: str
    platform: str | None = None
    title: str | None = None
    likes: int = 0
    views: int = 0
    comments: int = 0
    is_processed: bool = False
    created_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True

@router.get("/api/links/", response_model=List[LinkResponse])
def get_links(db: Session = Depends(get_db)):
    return db.query(SocialLink).order_by(SocialLink.created_at.desc()).all()

@router.post("/api/links/")
async def create_link(link: LinkCreate, db: Session = Depends(get_db)):
    try:
        # Check if link already exists
        existing_link = db.query(SocialLink).filter(SocialLink.url == link.url).first()
        if existing_link:
            raise HTTPException(status_code=400, detail="Link already exists")
        
        # Get parser and validate URL
        parser = parser_factory.get_parser(link.url)
        if not parser:
            raise HTTPException(status_code=400, detail="Unsupported URL")
        
        if not parser.validate_url(link.url):
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        # Create new link with initial data
        platform = 'youtube' if 'youtube.com' in link.url or 'youtu.be' in link.url else \
                  'tiktok' if 'tiktok.com' in link.url else \
                  'instagram' if 'instagram.com' in link.url else \
                  'facebook' if 'facebook.com' in link.url or 'fb.watch' in link.url else None
        
        if not platform:
            raise HTTPException(status_code=400, detail="Unsupported platform")
        
        db_link = SocialLink(
            url=link.url,
            platform=platform,
            is_processed=False,
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        
        db.add(db_link)
        db.commit()
        db.refresh(db_link)
        
        return {"message": "Link added successfully", "id": db_link.id}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/parse-link/")
async def parse_link(link: LinkCreate):
    try:
        # Get parser and parse URL
        metadata = await parser_factory.parse_url(link.url)
        return metadata
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 