from fastapi import FastAPI, Request, HTTPException, Depends, status, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel, HttpUrl
from backend.app.db.database import engine, Base, SessionLocal, get_db
from datetime import datetime, timedelta
from backend.app.parsers.parser_factory import ParserFactory
from backend.app.parsers.youtube_parser import YouTubeParser
from backend.app.parsers.tiktok_parser import TikTokParser
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional, List
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
import aiohttp
import json
import re
from bs4 import BeautifulSoup
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from logging.handlers import RotatingFileHandler
from backend.app.routers.stats import router as stats_router
<<<<<<< HEAD
from backend.app.routers.user_settings import router as user_settings_router
=======
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
from backend.app.utils.monday_sync import sync_link_to_monday
from backend.app.core.auth import (
    SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password, get_password_hash, create_access_token, get_current_user
)
import traceback
import asyncio
from sqlalchemy.sql import select
from sqlalchemy.orm import joinedload
from pydantic import ConfigDict
from backend.app.models.models import SocialLink, Platform, User, Company, Link, LinkMetrics, MondayConnection
<<<<<<< HEAD
from sqlalchemy.sql import text
=======
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize parser factory
parser_factory = ParserFactory()

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Initialize FastAPI app
app = FastAPI(title="Social Media Stats Dashboard", debug=True)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="backend/app/static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="../../templates")

# Mount Monday.com routes
app.include_router(stats_router)

<<<<<<< HEAD
# Mount user settings routes
app.include_router(user_settings_router)

=======
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
# Pydantic models for request/response
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

class CompanyBase(BaseModel):
    name: str
    
    class Config:
        orm_mode = True

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: int
    owner_id: int
    created_at: datetime
    monday_connected: bool = False

    class Config:
        orm_mode = True

class LinkBase(BaseModel):
    url: str
    platform: str
    title: Optional[str] = None

class LinkCreate(LinkBase):
    company_id: int

class LinkResponse(LinkBase):
    id: int
    user_id: int
    company_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class LinkMetricsResponse(BaseModel):
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class LinkWithMetricsResponse(BaseModel):
    id: int
    url: str
    platform: str | None = None
    title: str | None = None
    user_id: int
    company_id: int
    created_at: datetime
    monday_item_id: str | None = None
    metrics: LinkMetricsResponse | None = None
    monday_sync_status: str | None = None
    monday_error: str | None = None

    class Config:
        from_attributes = True
        orm_mode = True

class LinkSubmission(BaseModel):
    url: str
    company_id: int
    platform: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.instagram.com/reel/ABC123/",
                "company_id": 1
            }
        }

def validate_social_url(url: str) -> tuple[str, str]:
    """Validate and extract platform from social media URL."""
<<<<<<< HEAD
    logger.info(f"Validating social URL: '{url}'")
    if not url:
        raise ValueError("URL cannot be empty")
    url = url.strip()
    logger.info(f"Stripped URL: '{url}'")
=======
    if not url:
        raise ValueError("URL cannot be empty")
        
    url = url.strip()
    
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
    # YouTube URL patterns
    youtube_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=[\w-]+',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/[\w-]+',
        r'(?:https?:\/\/)?youtu\.be\/[\w-]+'
    ]
<<<<<<< HEAD
=======
    
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
    # TikTok URL patterns
    tiktok_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?tiktok\.com\/@[\w.-]+\/video\/\d+',
        r'(?:https?:\/\/)?(?:www\.)?tiktok\.com\/t\/[\w-]+',
        r'(?:https?:\/\/)?vm\.tiktok\.com\/[\w-]+'
    ]
<<<<<<< HEAD
=======
    
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
    # Instagram URL patterns
    instagram_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/(?:p|reel)\/[\w-]+(?:\/.*)?(?:\?.*)?$',
        r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/reels\/[\w-]+(?:\/.*)?(?:\?.*)?$',
        r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/(?:stories|tv)\/[\w-]+(?:\/.*)?(?:\?.*)?$'
    ]
<<<<<<< HEAD
    # Facebook URL patterns
    facebook_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?facebook\.com\/reel\/\d+',
=======
    
    # Facebook URL patterns
    facebook_patterns = [
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
        r'(?:https?:\/\/)?(?:www\.)?facebook\.com\/[\w.-]+\/videos\/\d+',
        r'(?:https?:\/\/)?(?:www\.)?facebook\.com\/watch\/\?v=\d+',
        r'(?:https?:\/\/)?(?:www\.)?fb\.watch\/[\w-]+'
    ]
<<<<<<< HEAD
    # Check each platform's patterns
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            logger.info(f"Matched YouTube pattern: {pattern}")
            return url, "youtube"
    for pattern in tiktok_patterns:
        if re.match(pattern, url):
            logger.info(f"Matched TikTok pattern: {pattern}")
            return url, "tiktok"
    for pattern in instagram_patterns:
        if re.match(pattern, url):
            logger.info(f"Matched Instagram pattern: {pattern}")
            return url, "instagram"
    for pattern in facebook_patterns:
        if re.match(pattern, url):
            logger.info(f"Matched Facebook pattern: {pattern}")
            return url, "facebook"
    logger.error(f"No pattern matched for URL: '{url}'")
=======
    
    # Check each platform's patterns
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return url, "youtube"
            
    for pattern in tiktok_patterns:
        if re.match(pattern, url):
            return url, "tiktok"
            
    for pattern in instagram_patterns:
        if re.match(pattern, url):
            return url, "instagram"
            
    for pattern in facebook_patterns:
        if re.match(pattern, url):
            return url, "facebook"
    
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
    raise ValueError("Invalid social media URL. Please provide a valid YouTube, TikTok, Instagram, or Facebook URL.")

def determine_platform(url: str) -> str:
    """Determine the platform from the URL."""
    try:
        _, platform = validate_social_url(url)
        return platform
    except ValueError:
        return "Unknown"

async def parse_social_link(url: str, platform: Optional[str] = None):
    """Parse social media link to extract metrics."""
    if not platform:
        platform = determine_platform(url)
        
    parser = parser_factory.get_parser(platform)
    if not parser:
        raise ValueError(f"Unsupported platform: {platform}")
        
    return await parser.parse(url)

def create_test_user(db: Session):
    """Create a test user if it doesn't exist."""
    test_user = db.query(User).filter(User.username == "testuser").first()
    if not test_user:
        logger.info("Creating test user...")
        hashed_password = get_password_hash("testpassword123")
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hashed_password
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        logger.info("Test user created successfully")
    return test_user

@app.on_event("startup")
async def startup_event():
    """Initialize services and create test user on startup."""
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    # Initialize database
    from backend.app.db.database import init_db
    init_db()
    
    # Initialize parser factory
    global parser_factory
    parser_factory = ParserFactory()
    
    # Create test user and company
    db = SessionLocal()
    try:
        # Create test user
        test_user = create_test_user(db)
        
        # Create test company if it doesn't exist
        test_company = db.query(Company).filter(Company.owner_id == test_user.id).first()
        if not test_company:
            logger.info("Creating test company...")
            test_company = Company(
                name="Test Company",
                owner_id=test_user.id
            )
            db.add(test_company)
            db.commit()
            db.refresh(test_company)
            logger.info("Test company created successfully")
    finally:
        db.close()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    logger.debug(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.debug(f"Response: {response.status_code}")
    return response

@app.get("/")
async def root(request: Request):
    # Check for token in cookies first
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
        
    try:
        # Verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return RedirectResponse(url="/login")
            
        # Token is valid, redirect to companies page
        return RedirectResponse(url="/companies")
    except JWTError:
        return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

async def process_single_link(link: Link, db: Session):
    """Process a single link to update its metrics."""
    try:
        # Get the appropriate parser
        parser = parser_factory.get_parser(url=link.url, platform=link.platform)
        if not parser:
            logger.error(f"No parser found for platform: {link.platform} and url: {link.url}")
            return
        # Parse the link to get metrics
        metrics = await parser.parse_url(link.url)
        if not metrics:
            logger.error(f"Failed to parse link: {link.url}")
            return
        
        # Update or create metrics in the database
        link_metrics = db.query(LinkMetrics).filter(LinkMetrics.link_id == link.id).first()
        
        if not link_metrics:
            link_metrics = LinkMetrics(link_id=link.id)
            db.add(link_metrics)
            
        # Update metrics
        link_metrics.views = metrics.get('views', 0)
        link_metrics.likes = metrics.get('likes', 0)
        link_metrics.comments = metrics.get('comments', 0)
        link_metrics.updated_at = datetime.utcnow()
        
        # Commit changes
        db.commit()
        logger.info(f"Updated metrics for link {link.id}: {metrics}")
            
    except Exception as e:
        logger.error(f"Error processing link {link.id}: {str(e)}\n{traceback.format_exc()}")
        db.rollback()

@app.post("/api/links/", response_model=LinkWithMetricsResponse)
async def add_link(
    link: LinkSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
<<<<<<< HEAD
    """Add a new social media link with parsing first."""
=======
    """Add a new social media link."""
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
    try:
        # Log the raw request body
        logger.info(f"Received link submission: {link.dict()}")
        
        # Validate and determine platform
        try:
            url, platform = validate_social_url(link.url)
            logger.info(f"Validated URL: {url}, Platform: {platform}")
        except ValueError as e:
            logger.error(f"URL validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
        # Verify company exists and user has access
        company = db.query(Company).filter(Company.id == link.company_id).first()
        if not company:
            logger.error(f"Company not found: {link.company_id}")
            raise HTTPException(status_code=404, detail="Company not found")
        if company.owner_id != current_user.id:
            logger.error(f"User {current_user.id} not authorized for company {link.company_id}")
            raise HTTPException(status_code=403, detail="Not authorized to add links to this company")
        
<<<<<<< HEAD
        # Parse the link FIRST and wait for response
        parsed_title = None
        parsed_metrics = None
        try:
            logger.info(f"Starting parser for URL: {url}")
            parser = parser_factory.get_parser(url=url, platform=platform)
            if parser:
                logger.info(f"Parser found: {type(parser).__name__}")
                parsed = await parser.parse_url(url)
                logger.info(f"Parser response received: {parsed}")
                
                parsed_title = parsed.get("title")
                parsed_metrics = {
                    'views': parsed.get('views', 0),
                    'likes': parsed.get('likes', 0),
                    'comments': parsed.get('comments', 0)
                }
                logger.info(f"Parsed title: {parsed_title}")
                logger.info(f"Parsed metrics: {parsed_metrics}")
                
                # If title is empty or None, try to create a fallback title
                if not parsed_title or parsed_title.strip() == "":
                    # Create a fallback title based on platform and URL
                    if platform == "youtube":
                        parsed_title = "YouTube Video"
                    elif platform == "tiktok":
                        parsed_title = "TikTok Video"
                    elif platform == "instagram":
                        parsed_title = "Instagram Post"
                    elif platform == "facebook":
                        parsed_title = "Facebook Post"
                    else:
                        parsed_title = f"{platform.title()} Content"
                    
                    logger.info(f"Using fallback title: {parsed_title}")
            else:
                logger.warning(f"No parser found for url={url}, platform={platform}")
                # Create a fallback title
                parsed_title = f"{platform.title()} Content"
                parsed_metrics = {'views': 0, 'likes': 0, 'comments': 0}
        except Exception as e:
            logger.error(f"Error parsing link: {str(e)}")
            # Create a fallback title even if parsing fails
            parsed_title = f"{platform.title()} Content"
            parsed_metrics = {'views': 0, 'likes': 0, 'comments': 0}
            logger.info(f"Using fallback title after error: {parsed_title}")
        
        # NOW create the link in database after parsing is complete
=======
        # Create new link
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
        try:
            new_link = Link(
                url=url,
                platform=platform.lower(),  # Ensure platform is lowercase
                user_id=current_user.id,
<<<<<<< HEAD
                company_id=link.company_id,
                title=parsed_title
=======
                company_id=link.company_id
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
            )
            db.add(new_link)
            db.commit()
            db.refresh(new_link)
            logger.info(f"Created new link with ID: {new_link.id}")
            
<<<<<<< HEAD
            # Create metrics with the parsed data
            metrics = LinkMetrics(
                link_id=new_link.id,
                views=parsed_metrics['views'],
                likes=parsed_metrics['likes'],
                comments=parsed_metrics['comments']
=======
            # Create initial metrics
            metrics = LinkMetrics(
                link_id=new_link.id,
                views=0,
                likes=0,
                comments=0
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
            )
            db.add(metrics)
            db.commit()
            db.refresh(new_link)
            
        except Exception as e:
            logger.error(f"Database error creating link: {str(e)}\n{traceback.format_exc()}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create link in database: {str(e)}")
        
<<<<<<< HEAD
=======
        # Process the link asynchronously
        try:
            asyncio.create_task(process_single_link(new_link, db))
            logger.info(f"Started async processing for link: {new_link.id}")
        except Exception as e:
            logger.error(f"Error starting async processing: {str(e)}\n{traceback.format_exc()}")
            # Don't raise here, as the link was created successfully
        
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
        # Sync to Monday.com
        monday_sync_status = 'not_configured'
        monday_error = None
        try:
            # Get Monday.com configuration
            monday_connection = db.query(MondayConnection).filter(
                MondayConnection.user_id == current_user.id,
                MondayConnection.company_id == link.company_id
            ).first()

            if monday_connection and monday_connection.board_id:
                logger.info(f"Syncing new link to Monday.com for link ID: {new_link.id}")
                
                # Get the updated link with metrics after async processing
                db.refresh(new_link)
                metrics = db.query(LinkMetrics).filter(LinkMetrics.link_id == new_link.id).first()
                
                # Prepare column values
                column_values = {
                    monday_connection.views_column_id: str(metrics.views if metrics else 0),
                    monday_connection.likes_column_id: str(metrics.likes if metrics else 0),
                    monday_connection.comments_column_id: str(metrics.comments if metrics else 0)
                }

                # Create item in Monday.com
                headers = {
                    "Authorization": monday_connection.api_token,
                    "Content-Type": "application/json"
                }
                
                # First, let's check if this is a subitems board by trying to get board info
                board_query = """
                query ($boardId: ID!) {
                    boards(ids: [$boardId]) {
                        id
                        name
                        board_kind
                    }
                }
                """
                
                board_variables = {
                    "boardId": monday_connection.board_id
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://api.monday.com/v2",
                        json={"query": board_query, "variables": board_variables},
                        headers=headers
                    ) as board_response:
                        board_data = await board_response.json()
                        is_subitems_board = False
                        
                        if "data" in board_data and board_data["data"]["boards"]:
                            board_info = board_data["data"]["boards"][0]
                            is_subitems_board = board_info.get("board_kind") == "subitems"
                            logger.info(f"Board type: {board_info.get('board_kind')}")
                        
                        # Use appropriate mutation based on board type
                        if is_subitems_board:
                            # For subitems boards, we need a parent item ID
                            # Let's try to find an existing parent item or create one
                            parent_query = """
                            query ($boardId: ID!) {
                                boards(ids: [$boardId]) {
                                    items {
                                        id
                                        name
                                    }
                                }
                            }
                            """
                            
                            async with session.post(
                                "https://api.monday.com/v2",
                                json={"query": parent_query, "variables": board_variables},
                                headers=headers
                            ) as parent_response:
                                parent_data = await parent_response.json()
                                parent_item_id = None
                                
                                if "data" in parent_data and parent_data["data"]["boards"]:
                                    items = parent_data["data"]["boards"][0].get("items", [])
                                    if items:
                                        parent_item_id = items[0]["id"]
                                        logger.info(f"Using parent item: {parent_item_id}")
                                
                                if parent_item_id:
                                    mutation = """
                                    mutation ($parentId: ID!, $itemName: String!, $columnValues: JSON!) {
                                        create_subitem (
                                            parent_item_id: $parentId,
                                            item_name: $itemName,
                                            column_values: $columnValues
                                        ) {
                                            id
                                        }
                                    }
                                    """
                                    
                                    variables = {
                                        "parentId": parent_item_id,
                                        "itemName": new_link.title or new_link.url,
                                        "columnValues": json.dumps(column_values)
                                    }
                                else:
                                    # No parent item found, can't create subitem
                                    monday_sync_status = 'error'
                                    monday_error = "No parent item found in subitems board. Please create a parent item first."
                                    logger.error(monday_error)
                                    return {
                                        "message": "Link added successfully",
                                        "id": new_link.id,
                                        "url": new_link.url,
                                        "platform": new_link.platform,
                                        "title": new_link.title,
                                        "user_id": new_link.user_id,
                                        "company_id": new_link.company_id,
                                        "created_at": new_link.created_at,
                                        "monday_item_id": new_link.monday_item_id,
                                        "metrics": {
                                            "views": metrics.views if metrics else 0,
                                            "likes": metrics.likes if metrics else 0,
                                            "comments": metrics.comments if metrics else 0,
                                            "updated_at": metrics.updated_at if metrics else None
                                        } if metrics else None,
                                        "monday_sync_status": monday_sync_status,
                                        "monday_error": monday_error
                                    }
                        else:
                            # Regular board
                            mutation = """
                            mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
                                create_item (
                                    board_id: $boardId,
                                    item_name: $itemName,
                                    column_values: $columnValues
                                ) {
                                    id
                                }
                            }
                            """
                            
                            variables = {
                                "boardId": monday_connection.board_id,
                                "itemName": new_link.title or new_link.url,
                                "columnValues": json.dumps(column_values)
                            }
                        
                        # Execute the mutation
                        async with session.post(
                            "https://api.monday.com/v2",
                            json={"query": mutation, "variables": variables},
                            headers=headers
                        ) as response:
                            if response.status != 200:
                                monday_sync_status = 'error'
                                monday_error = f"Failed to create Monday.com item (status {response.status})"
                                logger.error(monday_error)
                                data = await response.text()
                                logger.error(data)
                            else:
                                data = await response.json()
                                if "errors" in data:
                                    monday_sync_status = 'error'
                                    monday_error = data["errors"][0]["message"]
                                    logger.error(monday_error)
                                else:
                                    # Store Monday.com item ID
                                    if is_subitems_board:
                                        monday_item_id = data["data"]["create_subitem"]["id"]
                                    else:
                                        monday_item_id = data["data"]["create_item"]["id"]
                                    new_link.monday_item_id = monday_item_id
                                    db.commit()
                                    logger.info(f"Successfully created Monday.com item: {monday_item_id}")
                                    monday_sync_status = 'success'
            else:
                monday_sync_status = 'not_configured'
        except Exception as e:
            logger.error(f"Error syncing to Monday.com: {str(e)}", exc_info=True)
            monday_sync_status = 'error'
            monday_error = str(e)
        
        # Fetch metrics for the new link
        metrics = db.query(LinkMetrics).filter(LinkMetrics.link_id == new_link.id).first()
        return {
            "message": "Link added successfully",
            "id": new_link.id,
            "url": new_link.url,
            "platform": new_link.platform,
            "title": new_link.title,
            "user_id": new_link.user_id,
            "company_id": new_link.company_id,
            "created_at": new_link.created_at,
            "monday_item_id": new_link.monday_item_id,
            "metrics": {
                "views": metrics.views if metrics else 0,
                "likes": metrics.likes if metrics else 0,
                "comments": metrics.comments if metrics else 0,
                "updated_at": metrics.updated_at if metrics else None
            } if metrics else None,
            "monday_sync_status": monday_sync_status,
            "monday_error": monday_error
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding link: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/links/", response_model=List[LinkWithMetricsResponse])
async def get_links(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all links for a company."""
    try:
        logger.info(f"Fetching links for company_id: {company_id}")
        
        # Verify company exists and user has access
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            logger.error(f"Company not found: {company_id}")
            raise HTTPException(status_code=404, detail="Company not found")
            
        if company.owner_id != current_user.id:
            logger.error(f"User {current_user.id} not authorized for company {company_id}")
            raise HTTPException(status_code=403, detail="Not authorized to view this company's links")
        
        # Get links with metrics using eager loading
        links = (
            db.query(Link)
            .options(joinedload(Link.metrics))
            .filter(Link.company_id == company_id)
            .all()
        )
        
        # Convert to response format
        response = []
        for link in links:
            link_data = {
                "id": link.id,
                "url": link.url,
                "platform": link.platform,
                "title": link.title,
                "user_id": link.user_id,
                "company_id": link.company_id,
                "created_at": link.created_at,
                "monday_item_id": link.monday_item_id,
                "metrics": {
                    "views": link.metrics.views if link.metrics else 0,
                    "likes": link.metrics.likes if link.metrics else 0,
                    "comments": link.metrics.comments if link.metrics else 0,
                    "updated_at": link.metrics.updated_at if link.metrics else None
                } if link.metrics else None
            }
            response.append(link_data)
        
        return response
    except Exception as e:
        logger.error(f"Error getting links: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/debug/company/{company_id}")
async def debug_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Debug endpoint to check company and links state."""
    try:
        # Get company
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"error": "Company not found"}
            
        # Get all links
        links = db.query(Link).filter(Link.company_id == company_id).all()
        
        # Get all metrics
        metrics = db.query(LinkMetrics).join(Link).filter(Link.company_id == company_id).all()
        
        return {
            "company": {
                "id": company.id,
                "name": company.name,
                "owner_id": company.owner_id
            },
            "links": [
                {
                    "id": link.id,
                    "url": link.url,
                    "platform": link.platform,
                    "user_id": link.user_id,
                    "company_id": link.company_id,
                    "created_at": link.created_at.isoformat() if link.created_at else None,
                    "updated_at": link.updated_at.isoformat() if link.updated_at else None
                }
                for link in links
            ],
            "metrics": [
                {
                    "id": metric.id,
                    "link_id": metric.link_id,
                    "views": metric.views,
                    "likes": metric.likes,
                    "comments": metric.comments,
                    "updated_at": metric.updated_at.isoformat() if metric.updated_at else None
                }
                for metric in metrics
            ]
        }
    except Exception as e:
        logger.error(f"Debug endpoint error: {str(e)}\n{traceback.format_exc()}")
        return {"error": str(e)}

@app.get("/api/stats/")
async def get_stats():
    """Get overall statistics."""
    try:
        # This is a placeholder - implement actual stats logic
        return {"message": "Stats endpoint"}
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/update-metrics/")
async def update_metrics():
    """Update metrics for all links."""
    try:
        # This is a placeholder - implement actual update logic
        return {"message": "Metrics update endpoint"}
    except Exception as e:
        logger.error(f"Error updating metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/update-metrics/{link_id}")
async def update_single_metric(link_id: int):
    """Update metrics for a single link."""
    try:
        # This is a placeholder - implement actual update logic
        return {"message": f"Metrics update endpoint for link {link_id}"}
    except Exception as e:
        logger.error(f"Error updating metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/api/links/{link_id}")
async def delete_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a social media link."""
    try:
        # Get the link
        link = db.query(Link).filter(Link.id == link_id).first()
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
            
        # Verify user has access to the link
        if link.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this link")
            
        # Delete the link
        db.delete(link)
        db.commit()
        
        return {"message": "Link deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting link: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/companies", response_class=HTMLResponse)
async def companies_page(request: Request):
    return templates.TemplateResponse("companies.html", {"request": request})

@app.post("/api/companies/", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new company."""
    try:
        logger.info(f"Creating company: {company.name} for user: {current_user.id}")
        # Check if company name already exists for this user
        existing_company = db.query(Company).filter(
            Company.name == company.name,
            Company.owner_id == current_user.id
        ).first()
        
        if existing_company:
            logger.warning(f"Company name already exists: {company.name}")
            raise HTTPException(
                status_code=400,
                detail="A company with this name already exists"
            )
            
        # Create new company
        new_company = Company(
            name=company.name,
            owner_id=current_user.id
        )
        db.add(new_company)
        db.commit()
        db.refresh(new_company)
        logger.info(f"Company created successfully: {new_company.id}")
        return CompanyResponse.from_orm(new_company)
    except Exception as e:
        logger.error(f"Error creating company: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/companies/", response_model=List[CompanyResponse])
async def get_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all companies for the current user."""
    try:
        # Verify that the current_user exists in the database
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        companies = db.query(Company).filter(Company.owner_id == current_user.id).all()
        
        # Check Monday.com connection status for each company
        company_responses = []
        for company in companies:
            monday_connection = db.query(MondayConnection).filter(
                MondayConnection.company_id == company.id
            ).first()
            
            company_response = CompanyResponse.from_orm(company)
            company_response.monday_connected = monday_connection is not None
            company_responses.append(company_response)
        
        return company_responses
    except Exception as e:
        logger.error(f"Error getting companies: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Try to find user by username or email
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/statistics", response_class=HTMLResponse)
async def statistics_page(request: Request, company_id: Optional[int] = None):
    # Check for token in cookies first
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
        
    try:
        # Verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return RedirectResponse(url="/login")
            
        # Token is valid, render statistics page
        return templates.TemplateResponse(
            "statistics.html",
            {
                "request": request,
                "company_id": company_id
            }
        )
    except JWTError:
        return RedirectResponse(url="/login")

@app.delete("/api/companies/{company_id}")
async def delete_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a company."""
    try:
        # Get the company
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
            
        # Verify user has access to the company
        if company.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this company")
            
        # Delete the company
        db.delete(company)
        db.commit()
        
        return {"message": "Company deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting company: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/links/{link_id}/refresh")
async def refresh_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Refresh metrics for a single link."""
    try:
        # Get the link
        link = db.query(Link).filter(Link.id == link_id).first()
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
            
        # Verify user has access to the link
        if link.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to refresh this link")
            
        # Process the link
        await process_single_link(link, db)
        
        # Refresh the link to get updated metrics
        db.refresh(link)
        metrics = db.query(LinkMetrics).filter(LinkMetrics.link_id == link_id).first()
        
        # Sync to Monday.com
        monday_sync_status = 'not_configured'
        monday_error = None
        try:
            # Get Monday.com configuration
            monday_connection = db.query(MondayConnection).filter(
                MondayConnection.user_id == current_user.id,
                MondayConnection.company_id == link.company_id
            ).first()

            if monday_connection and monday_connection.board_id:
                logger.info(f"Syncing refreshed link to Monday.com for link ID: {link_id}")
                
                # Prepare column values
                column_values = {
                    monday_connection.views_column_id: str(metrics.views if metrics else 0),
                    monday_connection.likes_column_id: str(metrics.likes if metrics else 0),
                    monday_connection.comments_column_id: str(metrics.comments if metrics else 0)
                }

                if link.monday_item_id:
                    # Update existing item
                    headers = {
                        "Authorization": monday_connection.api_token,
                        "Content-Type": "application/json"
                    }
                    
                    mutation = """
                    mutation ($itemId: ID!, $columnValues: JSON!) {
                        change_multiple_column_values (
                            item_id: $itemId,
                            board_id: %s,
                            column_values: $columnValues
                        ) {
                            id
                        }
                    }
                    """ % monday_connection.board_id
                    
                    variables = {
                        "itemId": link.monday_item_id,
                        "columnValues": json.dumps(column_values)
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            "https://api.monday.com/v2",
                            json={"query": mutation, "variables": variables},
                            headers=headers
                        ) as response:
                            if response.status != 200:
                                monday_sync_status = 'error'
                                monday_error = f"Failed to update Monday.com item (status {response.status})"
                                logger.error(monday_error)
                                data = await response.text()
                                logger.error(data)
                            else:
                                data = await response.json()
                                if "errors" in data:
                                    monday_sync_status = 'error'
                                    monday_error = data["errors"][0]["message"]
                                    logger.error(monday_error)
                                else:
                                    logger.info(f"Successfully updated Monday.com item: {link.monday_item_id}")
                                    monday_sync_status = 'success'
                else:
                    # Create new item - check if it's a subitems board
                    headers = {
                        "Authorization": monday_connection.api_token,
                        "Content-Type": "application/json"
                    }
                    
                    # First, let's check if this is a subitems board by trying to get board info
                    board_query = """
                    query ($boardId: ID!) {
                        boards(ids: [$boardId]) {
                            id
                            name
                            board_kind
                        }
                    }
                    """
                    
                    board_variables = {
                        "boardId": monday_connection.board_id
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            "https://api.monday.com/v2",
                            json={"query": board_query, "variables": board_variables},
                            headers=headers
                        ) as board_response:
                            board_data = await board_response.json()
                            is_subitems_board = False
                            
                            if "data" in board_data and board_data["data"]["boards"]:
                                board_info = board_data["data"]["boards"][0]
                                is_subitems_board = board_info.get("board_kind") == "subitems"
                                logger.info(f"Board type: {board_info.get('board_kind')}")
                            
                            # Use appropriate mutation based on board type
                            if is_subitems_board:
                                # For subitems boards, we need a parent item ID
                                # Let's try to find an existing parent item or create one
                                parent_query = """
                                query ($boardId: ID!) {
                                    boards(ids: [$boardId]) {
                                        items {
                                            id
                                            name
                                        }
                                    }
                                }
                                """
                                
                                async with session.post(
                                    "https://api.monday.com/v2",
                                    json={"query": parent_query, "variables": board_variables},
                                    headers=headers
                                ) as parent_response:
                                    parent_data = await parent_response.json()
                                    parent_item_id = None
                                    
                                    if "data" in parent_data and parent_data["data"]["boards"]:
                                        items = parent_data["data"]["boards"][0].get("items", [])
                                        if items:
                                            parent_item_id = items[0]["id"]
                                            logger.info(f"Using parent item: {parent_item_id}")
                                
                                    if parent_item_id:
                                        mutation = """
                                        mutation ($parentId: ID!, $itemName: String!, $columnValues: JSON!) {
                                            create_subitem (
                                                parent_item_id: $parentId,
                                                item_name: $itemName,
                                                column_values: $columnValues
                                            ) {
                                                id
                                            }
                                        }
                                        """
                                        
                                        variables = {
                                            "parentId": parent_item_id,
                                            "itemName": link.title or link.url,
                                            "columnValues": json.dumps(column_values)
                                        }
                                    else:
                                        # No parent item found, can't create subitem
                                        monday_sync_status = 'error'
                                        monday_error = "No parent item found in subitems board. Please create a parent item first."
                                        logger.error(monday_error)
                                        return {
                                            "message": "Link refreshed successfully",
                                            "id": link.id,
                                            "url": link.url,
                                            "platform": link.platform,
                                            "title": link.title,
                                            "user_id": link.user_id,
                                            "company_id": link.company_id,
                                            "created_at": link.created_at,
                                            "monday_item_id": link.monday_item_id,
                                            "metrics": {
                                                "views": metrics.views if metrics else 0,
                                                "likes": metrics.likes if metrics else 0,
                                                "comments": metrics.comments if metrics else 0,
                                                "updated_at": metrics.updated_at if metrics else None
                                            } if metrics else None,
                                            "monday_sync_status": monday_sync_status,
                                            "monday_error": monday_error
                                        }
                            else:
                                # Regular board
                                mutation = """
                                mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
                                    create_item (
                                        board_id: $boardId,
                                        item_name: $itemName,
                                        column_values: $columnValues
                                    ) {
                                        id
                                    }
                                }
                                """
                                
                                variables = {
                                    "boardId": monday_connection.board_id,
                                    "itemName": link.title or link.url,
                                    "columnValues": json.dumps(column_values)
                                }
                            
                            # Execute the mutation
                            async with session.post(
                                "https://api.monday.com/v2",
                                json={"query": mutation, "variables": variables},
                                headers=headers
                            ) as response:
                                if response.status != 200:
                                    monday_sync_status = 'error'
                                    monday_error = f"Failed to create Monday.com item (status {response.status})"
                                    logger.error(monday_error)
                                    data = await response.text()
                                    logger.error(data)
                                else:
                                    data = await response.json()
                                    if "errors" in data:
                                        monday_sync_status = 'error'
                                        monday_error = data["errors"][0]["message"]
                                        logger.error(monday_error)
                                    else:
                                        # Store Monday.com item ID
                                        if is_subitems_board:
                                            monday_item_id = data["data"]["create_subitem"]["id"]
                                        else:
                                            monday_item_id = data["data"]["create_item"]["id"]
                                        link.monday_item_id = monday_item_id
                                        db.commit()
                                        logger.info(f"Successfully created Monday.com item: {monday_item_id}")
                                        monday_sync_status = 'success'
            else:
                monday_sync_status = 'not_configured'
        except Exception as e:
            logger.error(f"Error syncing to Monday.com: {str(e)}", exc_info=True)
            monday_sync_status = 'error'
            monday_error = str(e)
        
        return {
            "message": "Link refreshed successfully",
            "id": link.id,
            "url": link.url,
            "platform": link.platform,
            "title": link.title,
            "user_id": link.user_id,
            "company_id": link.company_id,
            "created_at": link.created_at,
            "monday_item_id": link.monday_item_id,
            "metrics": {
                "views": metrics.views if metrics else 0,
                "likes": metrics.likes if metrics else 0,
                "comments": metrics.comments if metrics else 0,
                "updated_at": metrics.updated_at if metrics else None
            } if metrics else None,
            "monday_sync_status": monday_sync_status,
            "monday_error": monday_error
        }
    except Exception as e:
        logger.error(f"Error refreshing link: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/monday")
async def monday_page(request: Request):
    return templates.TemplateResponse("monday.html", {"request": request})

@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request, company_id: int = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return templates.TemplateResponse("reports.html", {"request": request, "company_id": company_id})

@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.get("/api/reports/platform-performance")
async def get_platform_performance_report(
    company_id: int,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get platform performance report."""
    try:
        # Verify user has access to the company
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        if company.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this company")
            
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get links for the company
        links = db.query(Link).filter(Link.company_id == company_id).all()
        
        # Initialize platform stats
        platform_stats = {
            "YouTube": {"views": 0, "likes": 0, "comments": 0, "count": 0},
            "TikTok": {"views": 0, "likes": 0, "comments": 0, "count": 0},
            "Instagram": {"views": 0, "likes": 0, "comments": 0, "count": 0},
            "Facebook": {"views": 0, "likes": 0, "comments": 0, "count": 0}
        }
        
        # Aggregate metrics by platform
        for link in links:
            metrics = db.query(LinkMetrics).filter(
                LinkMetrics.link_id == link.id,
                LinkMetrics.updated_at >= start,
                LinkMetrics.updated_at <= end
            ).first()
            
            if metrics and link.platform in platform_stats:
                platform_stats[link.platform]["views"] += metrics.views or 0
                platform_stats[link.platform]["likes"] += metrics.likes or 0
                platform_stats[link.platform]["comments"] += metrics.comments or 0
                platform_stats[link.platform]["count"] += 1
        
        # Calculate averages
        for platform in platform_stats:
            if platform_stats[platform]["count"] > 0:
                platform_stats[platform]["avg_views"] = platform_stats[platform]["views"] / platform_stats[platform]["count"]
                platform_stats[platform]["avg_likes"] = platform_stats[platform]["likes"] / platform_stats[platform]["count"]
                platform_stats[platform]["avg_comments"] = platform_stats[platform]["comments"] / platform_stats[platform]["count"]
            else:
                platform_stats[platform]["avg_views"] = 0
                platform_stats[platform]["avg_likes"] = 0
                platform_stats[platform]["avg_comments"] = 0
        
        return platform_stats
    except Exception as e:
        logger.error(f"Error getting platform performance report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/reports/engagement-analysis")
async def get_engagement_analysis_report(
    company_id: int,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get engagement analysis report."""
    try:
        # Verify user has access to the company
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        if company.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this company")
            
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get links for the company
        links = db.query(Link).filter(Link.company_id == company_id).all()
        
        # Initialize engagement stats
        engagement_stats = {
            "total_views": 0,
            "total_likes": 0,
            "total_comments": 0,
            "total_links": len(links),
            "engagement_rate": 0
        }
        
        # Aggregate metrics
        for link in links:
            metrics = db.query(LinkMetrics).filter(
                LinkMetrics.link_id == link.id,
                LinkMetrics.updated_at >= start,
                LinkMetrics.updated_at <= end
            ).first()
            
            if metrics:
                engagement_stats["total_views"] += metrics.views or 0
                engagement_stats["total_likes"] += metrics.likes or 0
                engagement_stats["total_comments"] += metrics.comments or 0
        
        # Calculate engagement rate
        if engagement_stats["total_views"] > 0:
            engagement_stats["engagement_rate"] = (
                (engagement_stats["total_likes"] + engagement_stats["total_comments"]) /
                engagement_stats["total_views"]
            ) * 100
        
        return engagement_stats
    except Exception as e:
        logger.error(f"Error getting engagement analysis report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/reports/growth-trends")
async def get_growth_trends_report(
    company_id: int,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get growth trends report."""
    try:
        # Verify user has access to the company
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        if company.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this company")
            
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get links for the company
        links = db.query(Link).filter(Link.company_id == company_id).all()
        
        # Initialize growth stats
        growth_stats = {
            "total_views": 0,
            "total_likes": 0,
            "total_comments": 0,
            "total_links": len(links),
            "growth_rate": 0
        }
        
        # Aggregate metrics
        for link in links:
            metrics = db.query(LinkMetrics).filter(
                LinkMetrics.link_id == link.id,
                LinkMetrics.updated_at >= start,
                LinkMetrics.updated_at <= end
            ).first()
            
            if metrics:
                growth_stats["total_views"] += metrics.views or 0
                growth_stats["total_likes"] += metrics.likes or 0
                growth_stats["total_comments"] += metrics.comments or 0
        
        # Calculate growth rate
        if growth_stats["total_links"] > 0:
            growth_stats["growth_rate"] = (
                (growth_stats["total_views"] + growth_stats["total_likes"] + growth_stats["total_comments"]) /
                growth_stats["total_links"]
            ) * 100
        
        return growth_stats
    except Exception as e:
        logger.error(f"Error getting growth trends report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/monday/columns")
async def get_monday_columns(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get columns for a Monday.com board."""
    try:
        data = await request.json()
        api_token = data.get("api_token")
        board_id = data.get("board_id")
        if not api_token or not board_id:
            raise HTTPException(status_code=400, detail="API token and board ID are required")
        headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }
        query = """
        query ($board_id: [ID!]) {
            boards(ids: $board_id) {
                columns {
                    id
                    title
                    type
                }
            }
        }
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.monday.com/v2",
                json={"query": query, "variables": {"board_id": [board_id]}},
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    boards = result.get("data", {}).get("boards", [])
                    columns = boards[0]["columns"] if boards and "columns" in boards[0] else []
                    return {"columns": columns}
                else:
                    raise HTTPException(status_code=400, detail="Failed to fetch columns from Monday.com")
    except Exception as e:
        logger.error(f"Error getting Monday.com columns: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/monday/connect")
async def connect_monday(
    request: Request, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Connect a company to Monday.com."""
    try:
        data = await request.json()
        company_id = data.get("company_id")
        api_token = data.get("api_token")
        workspace_id = data.get("workspace_id")
        board_id = data.get("board_id")
        views_column_id = data.get("views_column_id")
        views_column_name = data.get("views_column_name")
        likes_column_id = data.get("likes_column_id")
        likes_column_name = data.get("likes_column_name")
        comments_column_id = data.get("comments_column_id")
        comments_column_name = data.get("comments_column_name")
        if not all([company_id, api_token, workspace_id, board_id]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        if company.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this company")
        existing_connection = db.query(MondayConnection).filter(
            MondayConnection.company_id == company_id
        ).first()
        if existing_connection:
            existing_connection.api_token = api_token
            existing_connection.workspace_id = workspace_id
            existing_connection.board_id = board_id
            existing_connection.views_column_id = views_column_id
            existing_connection.views_column_name = views_column_name
            existing_connection.likes_column_id = likes_column_id
            existing_connection.likes_column_name = likes_column_name
            existing_connection.comments_column_id = comments_column_id
            existing_connection.comments_column_name = comments_column_name
            existing_connection.updated_at = datetime.utcnow()
        else:
            monday_connection = MondayConnection(
                user_id=current_user.id,
                company_id=company_id,
                api_token=api_token,
                workspace_id=workspace_id,
                board_id=board_id,
                views_column_id=views_column_id,
                views_column_name=views_column_name,
                likes_column_id=likes_column_id,
                likes_column_name=likes_column_name,
                comments_column_id=comments_column_id,
                comments_column_name=comments_column_name
            )
            db.add(monday_connection)
        db.commit()
        return {"message": "Monday.com connection established successfully"}
    except Exception as e:
        logger.error(f"Error connecting to Monday.com: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/monday/workspaces")
async def get_monday_workspaces(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Monday.com workspaces using API token."""
    try:
        data = await request.json()
        api_token = data.get("api_token")
        
        if not api_token:
            raise HTTPException(status_code=400, detail="API token is required")
        
        # Make request to Monday.com API to get workspaces
        headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }
        
        query = """
        query {
            workspaces {
                id
                name
            }
        }
        """
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.monday.com/v2",
                json={"query": query},
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    workspaces = result.get("data", {}).get("workspaces", [])
                    return {"workspaces": workspaces}
                else:
                    raise HTTPException(status_code=400, detail="Failed to fetch workspaces from Monday.com")
                    
    except Exception as e:
        logger.error(f"Error getting Monday.com workspaces: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/monday/boards")
async def get_monday_boards(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Monday.com boards for a workspace."""
    try:
        data = await request.json()
        workspace_id = data.get("workspace_id")
        api_token = data.get("api_token")
        
        if not all([workspace_id, api_token]):
            raise HTTPException(status_code=400, detail="Workspace ID and API token are required")
        
        # Make request to Monday.com API to get boards
        headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }
        
        query = """
        query ($workspace_id: [ID!]) {
            boards(workspace_ids: $workspace_id) {
                id
                name
                board_kind
            }
        }
        """
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.monday.com/v2",
                json={"query": query, "variables": {"workspace_id": [workspace_id]}},
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    boards = result.get("data", {}).get("boards", [])
                    return {"boards": boards}
                else:
                    raise HTTPException(status_code=400, detail="Failed to fetch boards from Monday.com")
                    
    except Exception as e:
        logger.error(f"Error getting Monday.com boards: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/monday/items")
async def get_monday_items(
    board_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Monday.com items for a board."""
    try:
        # This is a placeholder - implement actual Monday.com item fetching logic
        return {"message": "Monday.com items endpoint"}
    except Exception as e:
        logger.error(f"Error getting Monday.com items: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/monday/verify_token", response_model=dict)
async def verify_monday_token(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify Monday.com token."""
    try:
        # This is a placeholder - implement actual Monday.com token verification logic
        return {"message": "Monday.com token verification endpoint"}
    except Exception as e:
        logger.error(f"Error verifying Monday.com token: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/monday/config")
async def monday_config_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return templates.TemplateResponse("monday_config.html", {"request": request})

@app.get("/monday/configured", response_class=HTMLResponse)
async def monday_configured_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return templates.TemplateResponse("monday_configured.html", {"request": request})

@app.get("/api/companies/{company_id}/stats")
async def get_company_stats(company_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get statistics for a specific company."""
    try:
        # Verify user has access to the company
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        if company.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this company")
            
        # Get links for the company
        links = db.query(Link).filter(Link.company_id == company_id).all()
        link_ids = [link.id for link in links]
        
        # Initialize stats
        stats = {
            "total_views": 0,
            "total_likes": 0,
            "total_comments": 0,
            "total_links": len(links),
            "platform_stats": {
                "YouTube": {"count": 0, "views": 0, "likes": 0, "comments": 0},
                "TikTok": {"count": 0, "views": 0, "likes": 0, "comments": 0},
                "Instagram": {"count": 0, "views": 0, "likes": 0, "comments": 0},
                "Facebook": {"count": 0, "views": 0, "likes": 0, "comments": 0}
            }
        }
        
<<<<<<< HEAD
        # Platform mapping for case-insensitive matching
        platform_mapping = {
            "youtube": "YouTube",
            "tiktok": "TikTok", 
            "instagram": "Instagram",
            "facebook": "Facebook"
        }
        
=======
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
        # Fetch all metrics for these links in one query
        metrics_list = db.query(LinkMetrics).filter(LinkMetrics.link_id.in_(link_ids)).all() if link_ids else []
        link_id_to_platform = {link.id: link.platform for link in links}
        
        for metrics in metrics_list:
            platform = link_id_to_platform.get(metrics.link_id)
<<<<<<< HEAD
            # Map platform to correct case
            platform_normalized = platform_mapping.get(platform.lower()) if platform else None
            if platform_normalized in stats["platform_stats"]:
                stats["platform_stats"][platform_normalized]["count"] += 1
                stats["platform_stats"][platform_normalized]["views"] += metrics.views or 0
                stats["platform_stats"][platform_normalized]["likes"] += metrics.likes or 0
                stats["platform_stats"][platform_normalized]["comments"] += metrics.comments or 0
=======
            if platform in stats["platform_stats"]:
                stats["platform_stats"][platform]["count"] += 1
                stats["platform_stats"][platform]["views"] += metrics.views or 0
                stats["platform_stats"][platform]["likes"] += metrics.likes or 0
                stats["platform_stats"][platform]["comments"] += metrics.comments or 0
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
                stats["total_views"] += metrics.views or 0
                stats["total_likes"] += metrics.likes or 0
                stats["total_comments"] += metrics.comments or 0
        
        return stats
    except Exception as e:
        logger.error(f"Error getting company stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/auth/register", response_model=UserBase)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user.email) | (User.username == user.username)
        ).first()
            
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email or username already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserBase.from_orm(db_user)
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}\n{traceback.format_exc()}")
<<<<<<< HEAD
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and CI/CD."""
    try:
        # Test database connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        ) 
=======
        raise HTTPException(status_code=500, detail="Internal server error") 
>>>>>>> 3f7391616262f0d9bb63bdfee4943e8983f27460
