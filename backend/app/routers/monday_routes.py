from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.db.database import get_db
from backend.app.models.models import MondayConnection, Link
from backend.app.utils.monday_sync import sync_link_to_monday
import logging

router = APIRouter(
    prefix="/monday",
    tags=["monday"],
    responses={404: {"description": "Not found"}},
)

@router.get("/connections")
async def get_monday_connections(db: Session = Depends(get_db)):
    """Get all Monday.com connections"""
    try:
        connections = db.query(MondayConnection).all()
        return connections
    except Exception as e:
        logging.error(f"Error getting Monday connections: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Monday connections"
        )

@router.post("/sync/{link_id}")
async def sync_link(
    link_id: int,
    db: Session = Depends(get_db)
):
    """Sync a specific link to Monday.com"""
    try:
        link = db.query(Link).filter(Link.id == link_id).first()
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link not found"
            )
        
        result = await sync_link_to_monday(link, db)
        return {"message": "Link synced successfully", "result": result}
    except Exception as e:
        logging.error(f"Error syncing link to Monday: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync link to Monday: {str(e)}"
        )

@router.post("/connections")
async def create_monday_connection(
    api_key: str,
    board_id: str,
    db: Session = Depends(get_db)
):
    """Create a new Monday.com connection"""
    try:
        connection = MondayConnection(
            api_key=api_key,
            board_id=board_id
        )
        db.add(connection)
        db.commit()
        db.refresh(connection)
        return connection
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating Monday connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Monday connection"
        )

@router.delete("/connections/{connection_id}")
async def delete_monday_connection(
    connection_id: int,
    db: Session = Depends(get_db)
):
    """Delete a Monday.com connection"""
    try:
        connection = db.query(MondayConnection).filter(MondayConnection.id == connection_id).first()
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection not found"
            )
        
        db.delete(connection)
        db.commit()
        return {"message": "Connection deleted successfully"}
    except Exception as e:
        db.rollback()
        logging.error(f"Error deleting Monday connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete Monday connection"
        ) 
