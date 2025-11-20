"""
Main Scheduler Entry Point
Orchestrates data collection jobs and scheduling.
"""

import logging
import schedule
import time
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlers.dining import fetch_menu
from crawlers.cse_site import fetch_announcements
from storage.mongo_writer import MongoDBWriter
from processors.cleaner import (
    clean_menu_data, 
    clean_announcement, 
    validate_menu_data, 
    validate_announcement
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pipeline.log')
    ]
)
logger = logging.getLogger(__name__)


class DataPipeline:
    """Main data pipeline orchestrator."""
    
    def __init__(self):
        """Initialize the pipeline."""
        self.db_writer = MongoDBWriter()
        self.sync_interval = int(os.getenv('SYNC_INTERVAL', 30))
        self.is_connected = False
        
    def connect_database(self) -> bool:
        """Connect to MongoDB."""
        if not self.is_connected:
            self.is_connected = self.db_writer.connect()
        return self.is_connected
    
    def job_sync_menu(self):
        """Job to sync dining menu data."""
        try:
            logger.info("="*60)
            logger.info("🍽️  Starting MENU sync job...")
            logger.info("="*60)
            
            # Fetch menu data
            menu_data = fetch_menu(use_mock=True)
            
            if not menu_data:
                logger.error("❌ Failed to fetch menu data")
                return
            
            # Clean data
            menu_data = clean_menu_data(menu_data)
            
            # Validate data
            if not validate_menu_data(menu_data):
                logger.error("❌ Menu data validation failed")
                return
            
            # Save to database
            if self.connect_database():
                success = self.db_writer.save_menu(menu_data)
                if success:
                    logger.info("✅ Menu sync completed successfully")
                else:
                    logger.error("❌ Failed to save menu to database")
            else:
                logger.error("❌ Database connection failed")
                
        except Exception as e:
            logger.error(f"❌ Error in menu sync job: {e}", exc_info=True)
    
    def job_sync_announcements(self):
        """Job to sync CSE announcements."""
        try:
            logger.info("="*60)
            logger.info("📰 Starting ANNOUNCEMENTS sync job...")
            logger.info("="*60)
            
            # Fetch announcements
            announcements = fetch_announcements(use_mock=True)
            
            if not announcements:
                logger.warning("⚠️  No announcements fetched")
                return
            
            # Clean and validate each announcement
            valid_announcements = []
            for announcement in announcements:
                cleaned = clean_announcement(announcement)
                if validate_announcement(cleaned):
                    valid_announcements.append(cleaned)
                else:
                    logger.warning(f"Skipping invalid announcement: {announcement.get('title', 'Unknown')}")
            
            if not valid_announcements:
                logger.warning("⚠️  No valid announcements to save")
                return
            
            # Save to database
            if self.connect_database():
                success = self.db_writer.save_announcements(valid_announcements)
                if success:
                    logger.info("✅ Announcements sync completed successfully")
                else:
                    logger.error("❌ Failed to save announcements to database")
            else:
                logger.error("❌ Database connection failed")
                
        except Exception as e:
            logger.error(f"❌ Error in announcements sync job: {e}", exc_info=True)
    
    def job_sync_all(self):
        """Combined job to sync all data sources."""
        start_time = datetime.now()
        
        logger.info("\n" + "🚀"*30)
        logger.info(f"🔄 FULL SYNC STARTED at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("🚀"*30 + "\n")
        
        # Sync menu
        self.job_sync_menu()
        
        # Small delay between jobs
        time.sleep(2)
        
        # Sync announcements
        self.job_sync_announcements()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "✅"*30)
        logger.info(f"✨ FULL SYNC COMPLETED in {duration:.2f} seconds")
        logger.info(f"⏰ Next sync in {self.sync_interval} seconds")
        logger.info("✅"*30 + "\n")
    
    def run(self):
        """Start the scheduler."""
        logger.info("🚀 Data Pipeline Starting...")
        logger.info(f"📊 MongoDB: {os.getenv('MONGO_DB_NAME')}")
        logger.info(f"⏱️  Sync Interval: {self.sync_interval} seconds")
        logger.info("="*60)
        
        # Test database connection
        if not self.connect_database():
            logger.error("❌ Failed to connect to MongoDB. Exiting...")
            return
        
        logger.info("✅ Successfully connected to MongoDB")
        
        # Run once immediately
        logger.info("🏃 Running initial sync...")
        self.job_sync_all()
        
        # Schedule recurring jobs
        schedule.every(self.sync_interval).seconds.do(self.job_sync_all)
        
        logger.info(f"⏰ Scheduler started. Running every {self.sync_interval} seconds")
        logger.info("Press Ctrl+C to stop\n")
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n🛑 Scheduler stopped by user")
            self.db_writer.close()
            logger.info("👋 Pipeline shutdown complete")


if __name__ == "__main__":
    pipeline = DataPipeline()
    pipeline.run()
