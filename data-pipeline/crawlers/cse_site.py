"""
CSE Department Announcements Crawler
Scrapes actual announcements from CSE department website.
"""

import logging
import requests
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class CseSiteCrawler:
    def __init__(self):
        self.base_url = "https://cse.akdeniz.edu.tr"
        self.list_url = "https://cse.akdeniz.edu.tr/tr/duyurular"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_links(self):
        """
        Scrapes the list page.
        Returns: List[Dict] -> [{'title': '...', 'link': '...'}]
        """
        logger.info(f"📡 Connecting to {self.list_url}...")
        
        try:
            response = requests.get(self.list_url, headers=self.headers, verify=False, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            results = []
            
            # --- NEW SELECTORS BASED ON SCREENSHOT ---
            # Look for the container with class 'list-announcement'
            list_group = soup.find("div", class_="list-announcement")
            
            if not list_group:
                logger.warning("⚠️ Could not find 'div.list-announcement'. Website structure might have changed.")
                return []

            # Get all <a> tags with class 'list-group-item'
            items = list_group.find_all("a", class_="list-group-item")
            
            for item in items:
                # 1. Extract Title (Text inside the <a> tag)
                title = item.get_text(strip=True)
                
                # 2. Extract Link
                relative_link = item.get('href')
                
                if not title or not relative_link:
                    continue

                # 3. Handle relative URLs
                if not relative_link.startswith("http"):
                    full_link = self.base_url + relative_link
                else:
                    full_link = relative_link
                
                results.append({
                    "title": title,
                    "link": full_link
                })
                
            logger.info(f"✅ Successfully found {len(results)} announcements.")
            return results

        except Exception as e:
            logger.error(f"❌ Error fetching links: {e}")
            return []