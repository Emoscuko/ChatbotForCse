"""
Main Scheduler Entry Point
Orchestrates Real Scraping and LLM Summarization.
"""

import logging
import schedule
import time
import os
import sys
from dotenv import load_dotenv

# --- PATH SETUP ---
# Add parent directory to path so we can import sibling folders
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# --- IMPORTS ---
# We use the classes we designed in previous steps
from crawlers.cse_site import CseSiteCrawler
from services.llm_client import PipelineLLM
from storage.mongo_writer import MongoWriter
# Placeholder for dining (we will do this later)
# from crawlers.dining import DiningCrawler 

# Load environment variables
load_dotenv()

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pipeline.log')
    ]
)
logger = logging.getLogger(__name__)

class DataPipeline:
    """Main data pipeline orchestrator."""
    
    def __init__(self):
        """Initialize the tools."""
        try:
            self.db_writer = MongoWriter()
            self.crawler = CseSiteCrawler()
            self.llm = PipelineLLM()
            self.sync_interval = int(os.getenv('SYNC_INTERVAL', 1800)) # Default 30 mins
            logger.info("✅ Pipeline tools initialized successfully.")
        except Exception as e:
            logger.critical(f"❌ Failed to init pipeline: {e}")
            sys.exit(1)

    def job_sync_menu(self):
        """Job to sync dining menu data."""
        # We will implement this later
        logger.info("🍽️  Checking Dining Menu... (Feature pending)")
        pass
    
    def job_sync_announcements(self):
        """Real job to sync CSE announcements with LLM."""
        try:
            logger.info("="*60)
            logger.info("📰 Starting ANNOUNCEMENTS sync job...")
            
            # 1. Fetch Links
            links = self.crawler.fetch_links()
            logger.info(f"🔍 Found {len(links)} announcements on the site.")
            
            new_count = 0
            
            for item in links:
                # 2. Check DB (Avoid duplicate work)
                if self.db_writer.is_exists(item['link']):
                    continue
                
                logger.info(f"✨ New Announcement found: {item['title']}")
                
                # 3. Fetch Content
                content = self.crawler.fetch_content(item['link'])
                
                # 4. Generate Summary (Using Gemini)
                summary = self.llm.generate_summary(content)
                
                # 5. Prepare Data
                data = {
                    "source_type": "website",
                    "title": item['title'],
                    "link": item['link'],
                    "original_content": content,
                    "short_summary": summary
                }
                
                # 6. Save
                self.db_writer.save_announcements(data)
                new_count += 1
                
                # Be nice to the server
                time.sleep(1)
            
            if new_count > 0:
                logger.info(f"✅ Processed and saved {new_count} new announcements.")
            else:
                logger.info("💤 No new announcements found.")
                
            logger.info("="*60)
                
        except Exception as e:
            logger.error(f"❌ Error in announcements sync job: {e}", exc_info=True)
    
    def job_sync_all(self):
        """Combined job."""
        self.job_sync_menu()
        self.job_sync_announcements()
    
    def run(self):
        """Start the scheduler."""
        logger.info("🚀 Data Pipeline Starting...")
        logger.info(f"⏱️  Sync Interval: {self.sync_interval} seconds")
        
        # Run once immediately on startup
        self.job_sync_all()
        
        # Schedule recurring jobs
        schedule.every(self.sync_interval).seconds.do(self.job_sync_all)
        
        logger.info(f"⏰ Scheduler active. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n🛑 Scheduler stopped by user")

if __name__ == "__main__":
    pipeline = DataPipeline()
    pipeline.run()