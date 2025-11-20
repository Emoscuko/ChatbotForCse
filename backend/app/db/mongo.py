from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

# Configure logging to track connection status
logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db = MongoDB()

async def connect_to_mongo():
    """
    Initializes the MongoDB connection and stores it in the global db instance.
    """
    try:
        db.client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING)
        db.db = db.client[settings.MONGO_DB_NAME]
        
        # Ping the database to ensure connection is successful
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB.")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    """
    Closes the MongoDB connection.
    """
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed.")
