from backend.app.db.database import SessionLocal
from backend.app.models.models import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_users():
    try:
        session = SessionLocal()
        users = session.query(User.id, User.username, User.email).all()
        logger.info("Users in database:")
        for user in users:
            logger.info(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
    except Exception as e:
        logger.error(f"Error checking users: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    check_users() 