

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    try:
        mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
        mongodb.database = mongodb.client[settings.mongodb_database]
        
        # Create indexes
        await mongodb.database.messages.create_index([("chat_id", ASCENDING), ("timestamp", ASCENDING)])
        await mongodb.database.chats.create_index([("created_at", ASCENDING)])
        
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client is not None:
        mongodb.client.close()
        logger.info("Disconnected from MongoDB")

def get_database():
    return mongodb.database