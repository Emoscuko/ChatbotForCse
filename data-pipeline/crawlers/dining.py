import logging
import requests
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings for university site
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class DiningCrawler:
    def __init__(self):
        # The URL you provided
        self.menu_page_url = "[https://sks.akdeniz.edu.tr/tr/haftalik_yemek_listesi-6391](https://sks.akdeniz.edu.tr/tr/haftalik_yemek_listesi-6391)"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_menu_image(self) -> bytes:
        """
        Scrapes the SKS page, finds the menu image inside .article-text, and downloads it.
        """
        logger.info(f"🍽️  Connecting to {self.menu_page_url}...")
        
        try:
            response = requests.get(self.menu_page_url, headers=self.headers, verify=False, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # --- SELECTOR LOGIC BASED ON SCREENSHOT ---
            # We look for the div with class 'article-text'
            article_text = soup.find("div", class_="article-text")
            
            if not article_text:
                logger.warning("⚠️  Could not find 'article-text' div.")
                return None

            # Find the image tag inside it
            img_tag = article_text.find("img")
            
            if not img_tag:
                logger.warning("⚠️  No image found inside article-text.")
                return None

            img_src = img_tag.get('src')
            
            # Handle relative URLs (though screenshot shows absolute)
            if not img_src.startswith("http"):
                # Check if it starts with / or not to join correctly
                base = "[https://sks.akdeniz.edu.tr](https://sks.akdeniz.edu.tr)"
                if not img_src.startswith("/"):
                    img_src = f"{base}/{img_src}"
                else:
                    img_src = f"{base}{img_src}"

            logger.info(f"📸 Found Menu Image URL: {img_src}")
            
            # Download the image bytes
            img_response = requests.get(img_src, headers=self.headers, verify=False, timeout=15)
            return img_response.content

        except Exception as e:
            logger.error(f"❌ Dining Scraper Error: {e}")
            return None