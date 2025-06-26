from fastapi import APIRouter, Request, HTTPException, Depends, status, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from backend.app.db.database import engine, Base, SessionLocal, get_db
from backend.app.models.models import User, MondayConnection, Company, Link, LinkMetrics
from sqlalchemy.orm import Session
from typing import Optional
from jose import JWTError, jwt
import aiohttp
import json
import logging
from backend.app.core.auth import SECRET_KEY, ALGORITHM, get_current_user
from datetime import datetime
from pydantic import BaseModel
from utils.url_validator import validate_social_url
from utils.social_parser import parse_social_link

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Create router
router = APIRouter()

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

@router.get("/monday")
async def monday_page(request: Request):
    """Monday.com integration page"""
    return templates.TemplateResponse("monday.html", {"request": request})

@router.post("/api/monday/connect")
async def connect_monday(request: Request, current_user: User = Depends(get_current_user)):
    """Connect to Monday.com"""
    try:
        data = await request.json()
        api_token = data.get("api_token")
        company_id = data.get("company_id")
        
        if not api_token:
            raise HTTPException(status_code=400, detail="API token is required")
        if not company_id:
            raise HTTPException(status_code=400, detail="Company ID is required")
            
        # Verify the token with Monday.com API
        headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }
        
        query = "{ me { id name } }"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.monday.com/v2",
                json={"query": query},
                headers=headers
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail="Invalid Monday.com API token")
                
                data = await response.json()
                if "errors" in data:
                    raise HTTPException(status_code=400, detail=data["errors"][0]["message"])
            
        # Store the Monday.com API token in the database
        db = SessionLocal()
        try:
            # Verify company exists and belongs to user
            company = db.query(Company).filter(
                Company.id == company_id,
                Company.owner_id == current_user.id
            ).first()
            
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")
            
            # Update or create Monday.com connection for the user and company
            monday_connection = db.query(MondayConnection).filter(
                MondayConnection.user_id == current_user.id,
                MondayConnection.company_id == company_id
            ).first()
            
            if monday_connection:
                monday_connection.api_token = api_token
                monday_connection.updated_at = datetime.utcnow()
            else:
                monday_connection = MondayConnection(
                    user_id=current_user.id,
                    company_id=company_id,
                    api_token=api_token
                )
                db.add(monday_connection)
            
            db.commit()
            return {"message": "Successfully connected to Monday.com"}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Database error in connect_monday: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in connect_monday: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/monday/workspaces")
async def get_monday_workspaces(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all workspaces from Monday.com"""
    try:
        # Get user's Monday.com API token for this company
        monday_connection = db.query(MondayConnection).filter(
            MondayConnection.user_id == current_user.id,
            MondayConnection.company_id == company_id
        ).first()
        
        if not monday_connection:
            raise HTTPException(status_code=400, detail="Please connect your Monday.com account first")
        
        # Make API request to Monday.com
        headers = {
            "Authorization": monday_connection.api_token,
            "Content-Type": "application/json"
        }
        
        query = """
        {
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
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Failed to fetch workspaces")
                
                data = await response.json()
                if "errors" in data:
                    raise HTTPException(status_code=400, detail=data["errors"][0]["message"])
                
                return data["data"]["workspaces"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/monday/boards")
async def get_monday_boards(
    workspace_id: int,
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all boards from a Monday.com workspace"""
    try:
        # Get user's Monday.com API token for this company
        monday_connection = db.query(MondayConnection).filter(
            MondayConnection.user_id == current_user.id,
            MondayConnection.company_id == company_id
        ).first()
        
        if not monday_connection:
            raise HTTPException(status_code=404, detail="No Monday.com connection found. Please connect your account first.")
        
        if not monday_connection.api_token:
            raise HTTPException(status_code=400, detail="Invalid Monday.com API token")
            
        logger.debug(f"Retrieved Monday.com connection for user {current_user.id}")
        
        # Make API request to Monday.com
        headers = {
            "Authorization": monday_connection.api_token,
            "Content-Type": "application/json"
        }
        
        query = """
        {
            boards(workspace_ids: [%d]) {
                id
                name
                state
                board_folder_id
                board_kind
                owner {
                    id
                    name
                }
            }
        }
        """ % workspace_id
        
        logger.debug(f"Making request to Monday.com API with query: {query}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.monday.com/v2",
                json={"query": query},
                headers=headers
            ) as response:
                logger.debug(f"Monday.com API response status: {response.status}")
                if response.status != 200:
                    error_msg = f"Failed to fetch boards: {response.status}"
                    logger.error(error_msg)
                    raise HTTPException(status_code=response.status, detail=error_msg)
                
                data = await response.json()
                logger.debug(f"Monday.com API response: {data}")
                
                if "errors" in data:
                    error_msg = data["errors"][0]["message"]
                    logger.error(f"Monday.com GraphQL Error: {error_msg}")
                    raise HTTPException(status_code=400, detail=error_msg)
                
                boards = data.get("data", {}).get("boards", [])
                logger.debug(f"Successfully retrieved {len(boards)} boards")
                return boards
                
    except Exception as e:
        error_msg = f"Internal server error: {str(e)}"
        logger.exception(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/api/monday/items")
async def get_monday_items(
    board_id: int,
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all items from a Monday.com board"""
    try:
        # Get user's Monday.com API token for this company
        monday_connection = db.query(MondayConnection).filter(
            MondayConnection.user_id == current_user.id,
            MondayConnection.company_id == company_id
        ).first()
        
        if not monday_connection:
            raise HTTPException(status_code=404, detail="No Monday.com connection found. Please connect your account first.")
        
        if not monday_connection.api_token:
            raise HTTPException(status_code=400, detail="Invalid Monday.com API token")
            
        logger.info("Retrieved Monday.com connection from database")
        logger.info(f"User ID: {current_user.id}")
        logger.info(f"Token exists: {bool(monday_connection.api_token)}")
        
        # Make request to Monday.com API
        query = """
        {
            boards (ids: ["%s"]) {
                id
                name
                items_page {
                    items {
                        id
                        name
                    }
                }
            }
        }
        """ % board_id
        
        logger.info(f"Making request to Monday.com API for board {board_id}")
        
        # Define headers for the API request
        headers = {
            "Authorization": monday_connection.api_token,
            "Content-Type": "application/json"
        }
        
        logger.debug(f"Request headers: {headers}")
        logger.debug(f"GraphQL Query: {query}")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    "https://api.monday.com/v2",
                    json={"query": query},
                    headers=headers
                ) as response:
                    logger.info(f"Monday.com API Response Status: {response.status}")
                    response_text = await response.text()
                    logger.debug(f"Response text: {response_text}")
                    
                    if response.status != 200:
                        error_msg = f"Failed to fetch items: {response_text}"
                        logger.error(error_msg)
                        raise HTTPException(
                            status_code=response.status,
                            detail=error_msg
                        )
                    
                    try:
                        data = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        error_msg = f"Failed to parse JSON response: {e}"
                        logger.error(error_msg)
                        raise HTTPException(
                            status_code=500,
                            detail=error_msg
                        )
                    
                    logger.debug(f"Monday.com API Response: {data}")
                    
                    if "errors" in data:
                        error_msg = data["errors"][0]["message"]
                        logger.error(f"Monday.com GraphQL Error: {error_msg}")
                        raise HTTPException(
                            status_code=400,
                            detail=error_msg
                        )
                    
                    boards_data = data.get("data", {}).get("boards", [])
                    if not boards_data:
                        error_msg = "No boards found in response"
                        logger.error(error_msg)
                        raise HTTPException(
                            status_code=404,
                            detail=error_msg
                        )
                    
                    items = boards_data[0].get("items_page", {}).get("items", [])
                    logger.info(f"Successfully retrieved {len(items)} items")
                    return items
                    
            except aiohttp.ClientError as e:
                error_msg = f"Failed to connect to Monday.com API: {str(e)}"
                logger.error(error_msg)
                raise HTTPException(
                    status_code=500,
                    detail=error_msg
                )
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Internal server error: {str(e)}"
        logger.exception(error_msg)
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

@router.get("/api/monday/verify-token", response_model=dict)
async def verify_monday_token(
    request: Request,
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify Monday.com API token"""
    try:
        # Get Monday.com connection for this company
        monday_connection = db.query(MondayConnection).filter(
            MondayConnection.user_id == current_user.id,
            MondayConnection.company_id == company_id
        ).first()
        
        if not monday_connection:
            return {"is_valid": False, "message": "No Monday.com connection found"}
            
        # Make API request to Monday.com to verify token
        headers = {
            "Authorization": monday_connection.api_token,
            "Content-Type": "application/json"
        }
        
        query = "{ me { id name } }"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.monday.com/v2",
                json={"query": query},
                headers=headers
            ) as response:
                if response.status != 200:
                    return {"is_valid": False, "message": "Invalid API token"}
                    
                data = await response.json()
                if "errors" in data:
                    return {"is_valid": False, "message": data["errors"][0]["message"]}
                    
                return {
                    "is_valid": True,
                    "message": "Token is valid",
                    "user": data["data"]["me"]
                }
                
    except Exception as e:
        return {"is_valid": False, "message": str(e)}

@router.get("/monday/config")
async def monday_config_page(
    request: Request,
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Monday.com configuration page"""
    try:
        # If no company_id is provided, use the first available company
        if company_id is None:
            company = db.query(Company).filter(Company.owner_id == current_user.id).first()
            if not company:
                raise HTTPException(status_code=400, detail="No companies found. Please create a company first.")
            company_id = company.id
        else:
            company = db.query(Company).filter(Company.id == company_id).first()
        company_name = company.name if company else ""
        # Get existing configuration for this company
        monday_connection = db.query(MondayConnection).filter(
            MondayConnection.user_id == current_user.id,
            MondayConnection.company_id == company_id
        ).first()
        return templates.TemplateResponse(
            "monday_config.html",
            {
                "request": request,
                "company_id": company_id,
                "company_name": company_name,
                "config": monday_connection
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in monday_config_page: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/monday/config")
async def save_monday_config(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save Monday.com configuration"""
    try:
        data = await request.json()
        company_id = data.get("company_id")
        api_token = data.get("api_token")
        workspace_id = data.get("workspace_id")
        workspace_name = data.get("workspace_name")
        board_id = data.get("board_id")
        board_name = data.get("board_name")
        item_id = data.get("item_id")
        item_name = data.get("item_name")
        
        # Get column mapping data
        views_column_id = data.get("views_column_id")
        views_column_name = data.get("views_column_name")
        likes_column_id = data.get("likes_column_id")
        likes_column_name = data.get("likes_column_name")
        comments_column_id = data.get("comments_column_id")
        comments_column_name = data.get("comments_column_name")
        
        if not company_id:
            raise HTTPException(status_code=400, detail="Company ID is required")
        if not api_token:
            raise HTTPException(status_code=400, detail="API token is required")
            
        # Get existing configuration or create new one
        monday_connection = db.query(MondayConnection).filter(
            MondayConnection.user_id == current_user.id,
            MondayConnection.company_id == company_id
        ).first()
        
        if not monday_connection:
            monday_connection = MondayConnection(
                user_id=current_user.id,
                company_id=company_id,
                api_token=api_token
            )
            db.add(monday_connection)
            
        # Update configuration
        monday_connection.api_token = api_token
        monday_connection.workspace_id = workspace_id
        monday_connection.workspace_name = workspace_name
        monday_connection.board_id = board_id
        monday_connection.board_name = board_name
        monday_connection.item_id = item_id
        monday_connection.item_name = item_name
        
        # Update column mappings
        monday_connection.views_column_id = views_column_id
        monday_connection.views_column_name = views_column_name
        monday_connection.likes_column_id = likes_column_id
        monday_connection.likes_column_name = likes_column_name
        monday_connection.comments_column_id = comments_column_id
        monday_connection.comments_column_name = comments_column_name
        
        monday_connection.updated_at = datetime.utcnow()
        
        try:
            db.commit()
            return {"message": "Configuration saved successfully"}
        except Exception as e:
            db.rollback()
            logger.error(f"Database error in save_monday_config: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in save_monday_config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/monday/columns")
async def get_monday_columns(
    board_id: int,
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all columns from a Monday.com board"""
    try:
        # Get user's Monday.com API token for this company
        monday_connection = db.query(MondayConnection).filter(
            MondayConnection.user_id == current_user.id,
            MondayConnection.company_id == company_id
        ).first()
        
        if not monday_connection:
            raise HTTPException(status_code=404, detail="No Monday.com connection found. Please connect your account first.")
        
        if not monday_connection.api_token:
            raise HTTPException(status_code=400, detail="Invalid Monday.com API token")
            
        logger.debug(f"Retrieved Monday.com connection for user {current_user.id}")
        
        # Make API request to Monday.com
        headers = {
            "Authorization": monday_connection.api_token,
            "Content-Type": "application/json"
        }
        
        query = """
        {
            boards(ids: [%d]) {
                columns {
                    id
                    title
                    type
                }
            }
        }
        """ % board_id
        
        logger.debug(f"Making request to Monday.com API with query: {query}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.monday.com/v2",
                json={"query": query},
                headers=headers
            ) as response:
                logger.debug(f"Monday.com API response status: {response.status}")
                if response.status != 200:
                    error_msg = f"Failed to fetch columns: {response.status}"
                    logger.error(error_msg)
                    raise HTTPException(status_code=response.status, detail=error_msg)
                
                data = await response.json()
                logger.debug(f"Monday.com API response: {data}")
                
                if "errors" in data:
                    error_msg = data["errors"][0]["message"]
                    logger.error(f"Monday.com GraphQL Error: {error_msg}")
                    raise HTTPException(status_code=400, detail=error_msg)
                
                columns = data.get("data", {}).get("boards", [{}])[0].get("columns", [])
                # Filter for number columns only
                number_columns = [col for col in columns if col["type"] in ["numeric", "numbers"]]
                logger.debug(f"Successfully retrieved {len(number_columns)} number columns")
                return number_columns
                
    except Exception as e:
        error_msg = f"Internal server error: {str(e)}"
        logger.exception(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

async def create_monday_item(
    board_id: str,
    item_name: str,
    column_values: dict,
    monday_connection: MondayConnection
) -> dict:
    """Create a new item in a Monday.com board with specified column values"""
    try:
        headers = {
            "Authorization": monday_connection.api_token,
            "Content-Type": "application/json"
        }
        
        # Convert column values to Monday.com format
        column_values_json = json.dumps(column_values)
        
        mutation = """
        mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
            create_item (
                board_id: $boardId,
                item_name: $itemName,
                column_values: $columnValues
            ) {
                id
                name
            }
        }
        """
        
        variables = {
            "boardId": board_id,
            "itemName": item_name,
            "columnValues": column_values_json
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.monday.com/v2",
                json={"query": mutation, "variables": variables},
                headers=headers
            ) as response:
                if response.status != 200:
                    error_msg = f"Failed to create item: {response.status}"
                    logger.error(error_msg)
                    raise HTTPException(status_code=response.status, detail=error_msg)
                
                data = await response.json()
                logger.debug(f"Monday.com API response: {data}")
                
                if "errors" in data:
                    error_msg = data["errors"][0]["message"]
                    logger.error(f"Monday.com GraphQL Error: {error_msg}")
                    raise HTTPException(status_code=400, detail=error_msg)
                
                return data["data"]["create_item"]
                
    except Exception as e:
        error_msg = f"Error creating Monday.com item: {str(e)}"
        logger.exception(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/api/links/")
async def add_link(
    link: LinkSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"[ADD_LINK] Starting to process link submission: {link.dict()}")
    try:
        company = db.query(Company).filter(
            Company.id == link.company_id,
            Company.owner_id == current_user.id
        ).first()
        if not company:
            logger.error(f"[ADD_LINK] Company {link.company_id} not found for user {current_user.id}")
            raise HTTPException(status_code=404, detail="Company not found")
        try:
            url = link.url.strip()
            if not url:
                raise ValueError("URL cannot be empty")
            logger.info(f"[ADD_LINK] Validating URL: {url}")
            url, platform = validate_social_url(url)
            logger.info(f"[ADD_LINK] URL validated. Platform detected: {platform}")
            existing_link = db.query(Link).filter(
                Link.url == url,
                Link.company_id == link.company_id
            ).first()
            if existing_link:
                logger.warning(f"[ADD_LINK] Link already exists: {url}")
                raise HTTPException(
                    status_code=400, 
                    detail="This link has already been added to this company"
                )
            logger.info(f"[ADD_LINK] Fetching stats for URL: {url}")
            stats = await parse_social_link(url)
            logger.info(f"[ADD_LINK] Stats fetched: {stats}")
            if not stats:
                logger.error("[ADD_LINK] Could not fetch link stats")
                raise ValueError("Could not fetch link stats")
            logger.info(f"[ADD_LINK] Creating link in database with title: {stats.get('title', '')}")
            db_link = Link(
                url=url,
                platform=platform,
                title=stats.get('title', ''),
                user_id=current_user.id,
                company_id=link.company_id
            )
            db.add(db_link)
            db.commit()
            db.refresh(db_link)
            logger.info(f"[ADD_LINK] Link created with ID: {db_link.id}")
            logger.info(f"[ADD_LINK] Creating metrics in database: views={stats.get('views', 0)}, likes={stats.get('likes', 0)}, comments={stats.get('comments', 0)}")
            db_metrics = LinkMetrics(
                link_id=db_link.id,
                views=stats.get('views', 0),
                likes=stats.get('likes', 0),
                comments=stats.get('comments', 0)
            )
            db.add(db_metrics)
            db.commit()
            logger.info(f"[ADD_LINK] Metrics created for link ID: {db_link.id}")

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
                    logger.info(f"[ADD_LINK] Syncing to Monday.com for link ID: {db_link.id}")
                    # Prepare column values
                    column_values = {
                        monday_connection.views_column_id: str(stats.get('views', 0)),
                        monday_connection.likes_column_id: str(stats.get('likes', 0)),
                        monday_connection.comments_column_id: str(stats.get('comments', 0))
                    }

                    # Create item in Monday.com
                    monday_item = await create_monday_item(
                        board_id=monday_connection.board_id,
                        item_name=stats.get('title', url),
                        column_values=column_values,
                        monday_connection=monday_connection
                    )

                    # Store Monday.com item ID
                    db_link.monday_item_id = monday_item['id']
                    db.commit()
                    logger.info(f"[ADD_LINK] Successfully synced to Monday.com with item ID: {monday_item['id']}")
                    monday_sync_status = 'success'
                else:
                    monday_sync_status = 'not_configured'
            except Exception as e:
                logger.error(f"[ADD_LINK] Error syncing to Monday.com: {str(e)}", exc_info=True)
                monday_sync_status = 'error'
                monday_error = str(e)

            return {
                "message": "Link added successfully",
                "id": db_link.id,
                "url": db_link.url,
                "platform": db_link.platform,
                "title": db_link.title,
                "user_id": db_link.user_id,
                "company_id": db_link.company_id,
                "created_at": db_link.created_at,
                "monday_item_id": db_link.monday_item_id,
                "metrics": {
                    "views": db_metrics.views if db_metrics else 0,
                    "likes": db_metrics.likes if db_metrics else 0,
                    "comments": db_metrics.comments if db_metrics else 0,
                    "updated_at": db_metrics.updated_at if db_metrics else None
                } if db_metrics else None,
                "stats": stats,
                "monday_sync_status": monday_sync_status,
                "monday_error": monday_error
            }
        except Exception as e:
            db.rollback()
            logger.error(f"[ADD_LINK] Database error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"[ADD_LINK] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/links/{link_id}/refresh")
async def refresh_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    link = db.query(Link).filter(
        Link.id == link_id,
        Link.user_id == current_user.id
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    try:
        # Debug: Print URL and platform before parsing
        logger.info(f"[REFRESH_LINK] Refreshing link ID: {link_id}, URL: {link.url}, Platform: {link.platform}")
        # Fetch new stats
        stats = await parse_social_link(link.url)
        logger.info(f"[REFRESH_LINK] Stats fetched: {stats}")
        if not stats:
            raise HTTPException(status_code=400, detail="Could not fetch link stats")
        # Update link title if changed
        link.title = stats.get('title', link.title)
        # Update or create metrics
        metrics = db.query(LinkMetrics).filter(LinkMetrics.link_id == link_id).first()
        if metrics:
            metrics.views = stats.get('views', 0)
            metrics.likes = stats.get('likes', 0)
            metrics.comments = stats.get('comments', 0)
            metrics.updated_at = datetime.utcnow()
        else:
            metrics = LinkMetrics(
                link_id=link_id,
                views=stats.get('views', 0),
                likes=stats.get('likes', 0),
                comments=stats.get('comments', 0)
            )
            db.add(metrics)
        db.commit()
        logger.info(f"[REFRESH_LINK] Metrics updated for link ID: {link_id}")

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
                logger.info(f"[REFRESH_LINK] Syncing to Monday.com for link ID: {link_id}")
                # Prepare column values
                column_values = {
                    monday_connection.views_column_id: str(stats.get('views', 0)),
                    monday_connection.likes_column_id: str(stats.get('likes', 0)),
                    monday_connection.comments_column_id: str(stats.get('comments', 0))
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
                                raise Exception(monday_error)
                            data = await response.json()
                            if "errors" in data:
                                monday_sync_status = 'error'
                                monday_error = data["errors"][0]["message"]
                                logger.error(monday_error)
                                raise Exception(monday_error)
                            logger.info(f"[REFRESH_LINK] Successfully updated Monday.com item: {link.monday_item_id}")
                            monday_sync_status = 'success'
                else:
                    # Create new item
                    monday_item = await create_monday_item(
                        board_id=monday_connection.board_id,
                        item_name=stats.get('title', link.url),
                        column_values=column_values,
                        monday_connection=monday_connection
                    )
                    # Store Monday.com item ID
                    link.monday_item_id = monday_item['id']
                    db.commit()
                    logger.info(f"[REFRESH_LINK] Successfully created Monday.com item: {monday_item['id']}")
                    monday_sync_status = 'success'
            else:
                monday_sync_status = 'not_configured'
        except Exception as e:
            logger.error(f"[REFRESH_LINK] Error syncing to Monday.com: {str(e)}", exc_info=True)
            if not monday_error:
                monday_sync_status = 'error'
                monday_error = str(e)

        return {
            "message": "Link metrics updated successfully",
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
    except ValueError as e:
        logger.error(f"[REFRESH_LINK] ValueError: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"[REFRESH_LINK] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 