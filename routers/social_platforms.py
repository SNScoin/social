from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.models.models import Platform

router = APIRouter(prefix="/platforms", tags=["platforms"])

@router.get("/")
async def get_platforms():
    return [{"name": platform.name, "value": platform.value} for platform in Platform] 