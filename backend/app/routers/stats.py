from backend.app.models.models import SocialLink, Platform
from backend.app.models.models import Link, LinkMetrics
from backend.app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime
from backend.app.models.schemas import LinkWithMetricsResponse
from backend.app.core.auth import get_current_user

router = APIRouter() 