"""
MongoDB Writer Module
Handles all database write operations with error handling and logging.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MongoDBWriter:
    """Handles MongoDB connection and write operations."""
    
    def __init__(self):
        """Initialize MongoDB connection."""
        self.connection_string = os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017')
        self.db_name = os.getenv('MONGO_DB_NAME', 'akdeniz_cse_db')
        self.client: Optional[MongoClient] = None
        self.db = None
        
    def connect(self) -> bool:
        """
        Establish connection to MongoDB.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            logger.info(f"Successfully connected to MongoDB: {self.db_name}")
            return True
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during MongoDB connection: {e}")
            return False
    
    def close(self):
        """Close MongoDB connection."""
        if self.client is not None:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def save_menu(self, menu_data: Dict) -> bool:
        """
        Save or update dining menu data.
        Upserts based on date to avoid duplicates.
        
        Args:
            menu_data: Dictionary containing menu information with 'date' key
            
        Returns:
            bool: True if operation successful, False otherwise
        """
        if self.db is None:
            logger.error("Database not connected. Call connect() first.")
            return False
        
        if not menu_data or 'date' not in menu_data:
            logger.error("Invalid menu data: 'date' field is required")
            return False
        
        try:
            collection = self.db['dining']
            
            # Add metadata
            menu_data['updated_at'] = datetime.utcnow()
            
            # Prepare update document without created_at
            update_doc = {k: v for k, v in menu_data.items() if k != 'created_at'}
            
            # Upsert based on date
            result = collection.update_one(
                {'date': menu_data['date']},
                {
                    '$set': update_doc,
                    '$setOnInsert': {'created_at': datetime.utcnow()}
                },
                upsert=True
            )
            
            if result.upserted_id:
                logger.info(f"✅ New menu inserted for date: {menu_data['date']}")
            elif result.modified_count > 0:
                logger.info(f"♻️  Menu updated for date: {menu_data['date']}")
            else:
                logger.info(f"ℹ️  No changes needed for menu on date: {menu_data['date']}")
            
            return True
            
        except OperationFailure as e:
            logger.error(f"MongoDB operation failed while saving menu: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while saving menu: {e}")
            return False
    
    def save_announcements(self, announcements: List[Dict]) -> bool:
        """
        Save or update multiple announcements.
        Upserts based on URL to avoid duplicates.
        
        Args:
            announcements: List of announcement dictionaries with 'url' key
            
        Returns:
            bool: True if operation successful, False otherwise
        """
        if self.db is None:
            logger.error("Database not connected. Call connect() first.")
            return False
        
        if not announcements:
            logger.warning("No announcements to save")
            return True
        
        try:
            collection = self.db['announcements']
            
            # Prepare bulk operations
            operations = []
            new_count = 0
            updated_count = 0
            
            for announcement in announcements:
                if 'url' not in announcement:
                    logger.warning(f"Skipping announcement without URL: {announcement.get('title', 'Unknown')}")
                    continue
                
                # Add metadata and prepare update document without created_at
                announcement['updated_at'] = datetime.utcnow()
                update_doc = {k: v for k, v in announcement.items() if k != 'created_at'}
                
                operations.append(
                    UpdateOne(
                        {'url': announcement['url']},
                        {
                            '$set': update_doc,
                            '$setOnInsert': {'created_at': datetime.utcnow()}
                        },
                        upsert=True
                    )
                )
            
            if not operations:
                logger.warning("No valid announcements to save")
                return False
            
            # Execute bulk write
            result = collection.bulk_write(operations, ordered=False)
            
            new_count = result.upserted_count
            updated_count = result.modified_count
            
            logger.info(f"📰 Announcements processed: {new_count} new, {updated_count} updated")
            
            if new_count > 0:
                logger.info(f"✅ Added {new_count} new announcement(s)")
            if updated_count > 0:
                logger.info(f"♻️  Updated {updated_count} existing announcement(s)")
            
            return True
            
        except OperationFailure as e:
            logger.error(f"MongoDB operation failed while saving announcements: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while saving announcements: {e}")
            return False
    
    def get_latest_menu(self) -> Optional[Dict]:
        """
        Retrieve the most recent menu entry.
        
        Returns:
            Dict or None: Latest menu data if found
        """
        if self.db is None:
            logger.error("Database not connected")
            return None
        
        try:
            collection = self.db['dining']
            result = collection.find_one(sort=[('date', -1)])
            return result
        except Exception as e:
            logger.error(f"Error retrieving latest menu: {e}")
            return None
    
    def get_recent_announcements(self, limit: int = 10) -> List[Dict]:
        """
        Retrieve recent announcements.
        
        Args:
            limit: Maximum number of announcements to return
            
        Returns:
            List of announcement dictionaries
        """
        if self.db is None:
            logger.error("Database not connected")
            return []
        
        try:
            collection = self.db['announcements']
            results = list(collection.find().sort('created_at', -1).limit(limit))
            return results
        except Exception as e:
            logger.error(f"Error retrieving announcements: {e}")
            return []


# Convenience functions for backward compatibility
_writer_instance = None

def get_writer() -> MongoDBWriter:
    """Get or create MongoDB writer instance."""
    global _writer_instance
    if _writer_instance is None:
        _writer_instance = MongoDBWriter()
        _writer_instance.connect()
    return _writer_instance


def save_menu(menu_data: Dict) -> bool:
    """Convenience function to save menu data."""
    writer = get_writer()
    return writer.save_menu(menu_data)


def save_announcements(announcements: List[Dict]) -> bool:
    """Convenience function to save announcements."""
    writer = get_writer()
    return writer.save_announcements(announcements)
