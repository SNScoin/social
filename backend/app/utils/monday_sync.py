import logging
import json
import aiohttp
import os
from datetime import datetime
from backend.app.models.models import MondayConnection, User, Link, LinkMetrics
from sqlalchemy.orm import Session

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create a file handler for Monday.com sync specific logs
file_handler = logging.FileHandler(os.path.join(log_dir, 'monday_sync.log'))
file_handler.setLevel(logging.DEBUG)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

async def sync_link_to_monday(link: Link, db: Session) -> dict:
    """
    Sync a link to Monday.com board
    """
    try:
        connection = db.query(MondayConnection).first()
        if not connection:
            raise Exception("No Monday.com connection found")

        item_data = {
            "name": link.title or link.url,
            "column_values": {
                "url": {"url": link.url, "text": link.title or link.url},
                "status": {"label": "Active" if getattr(link, 'is_active', True) else "Inactive"},
                "platform": {"label": getattr(getattr(link, 'platform', None), 'name', 'Unknown')},
                "metrics": {
                    "views": getattr(getattr(link, 'metrics', None), 'views', 0),
                    "likes": getattr(getattr(link, 'metrics', None), 'likes', 0),
                    "comments": getattr(getattr(link, 'metrics', None), 'comments', 0),
                    "shares": getattr(getattr(link, 'metrics', None), 'shares', 0)
                }
            }
        }

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": connection.api_key,
                "Content-Type": "application/json"
            }
            async with session.post(
                f"https://api.monday.com/v2/boards/{connection.board_id}/items",
                headers=headers,
                json={"item": item_data}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to sync to Monday.com: {error_text}")
                result = await response.json()
                return result
    except Exception as e:
        logging.error(f"Error syncing link to Monday.com: {str(e)}")
        raise 
