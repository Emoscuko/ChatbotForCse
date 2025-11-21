"""
Main Scheduler Entry Point
"""

import logging
import schedule
import time
import os
import sys
from dotenv import load_dotenv

# --- PATH SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# --- IMPORTS ---
from crawlers.cse_site import CseSiteCrawler
from crawlers.dining import DiningCrawler
from services.llm_service import PipelineLLM
from storage.mongo_writer import MongoWriter

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
        try:
            self.db_writer = MongoWriter()
            self.crawler = CseSiteCrawler()
            self.dining_crawler = DiningCrawler()
            self.llm = PipelineLLM()
            
            self.sync_interval = int(os.getenv('SYNC_INTERVAL', 1800)) 
            logger.info("✅ Pipeline tools initialized successfully.")
        except Exception as e:
            logger.critical(f"❌ Failed to init pipeline: {e}")
            sys.exit(1)

    def job_sync_menu(self):
        """Job to sync dining menu data from Image."""
        try:
            logger.info("🍽️  Starting DINING MENU sync job...")
            
            image_bytes = self.dining_crawler.fetch_menu_image()
            
            if not image_bytes:
                logger.warning("⚠️  No menu image found.")
                return

            logger.info("🧠 Sending image to Gemini...")
            menu_json_list = self.llm.extract_menu_from_image(image_bytes)
            
            if not menu_json_list:
                logger.error("❌ LLM failed to extract JSON.")
                return
            logger.info(f"🔍 Gemini Response Data: {menu_json_list}")
            self.db_writer.save_menu(menu_json_list)
            
        except Exception as e:
            logger.error(f"❌ Error in menu sync job: {e}", exc_info=True)
    
    def job_sync_announcements(self):
        """
        Simplified Job: Syncs Titles and Links only.
        No LLM, No Detail Scraping.
        """
        try:
            logger.info("="*60)
            logger.info("📰 Starting ANNOUNCEMENTS sync job...")
            
            # 1. Fetch Titles and Links (Using new logic)
            links = self.crawler.fetch_links()
            logger.info(f"🔍 Found {len(links)} announcements on the site.")
            
            new_count = 0
            
            for item in links:
                # 2. Check DB (Avoid duplicate work)
                if self.db_writer.is_exists(item['link']):
                    continue
                
                logger.info(f"✨ New Announcement: {item['title']}")
                
                # 3. Prepare Data
                # Since we don't have a summary, we use the Title as the summary
                # or leave 'original_content' empty.
                data = {
                    "source_type": "website",
                    "title": item['title'],
                    "link": item['link'],
                }
                
                # 4. Save directly
                self.db_writer.save_announcements(data)
                new_count += 1
            
            if new_count > 0:
                logger.info(f"✅ Saved {new_count} new announcements.")
            else:
                logger.info("💤 No new announcements found.")
                
            logger.info("="*60)
                
        except Exception as e:
            logger.error(f"❌ Error in announcements sync job: {e}", exc_info=True)
    
    def job_sync_all(self):
        self.job_sync_menu()
        self.job_sync_announcements()
    
    def run(self):
        logger.info("🚀 Data Pipeline Starting...")
        self.job_sync_all()
        schedule.every(self.sync_interval).seconds.do(self.job_sync_all)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n🛑 Scheduler stopped by user")

if __name__ == "__main__":
    pipeline = DataPipeline()
    pipeline.run()