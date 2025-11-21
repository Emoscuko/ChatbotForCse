"""
CSE Department Announcements Crawler
Scrapes actual announcements from CSE department website.
Compatible with Akdeniz University Drupal infrastructure.
"""

import logging
import requests
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings (Common issue with university sites)
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
        Step 1: Go to the list page and get all announcement Titles and Links.
        Returns: List[Dict] -> [{'title': '...', 'link': '...'}]
        """
        logger.info(f"📡 Connecting to {self.list_url}...")
        
        try:
            response = requests.get(self.list_url, headers=self.headers, verify=False, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            results = []
            
            # Drupal specific selectors for Akdeniz site
            content_div = soup.find("div", class_="view-content")
            
            if not content_div:
                logger.warning("⚠️  Could not find announcement list container (.view-content)")
                return []

            rows = content_div.find_all("div", class_="views-row")
            
            for row in rows:
                # Extract Title and Link
                title_div = row.find("div", class_="views-field-title")
                if not title_div: continue
                
                link_tag = title_div.find("a")
                if not link_tag: continue

                title = link_tag.text.strip()
                relative_link = link_tag['href']
                
                # Ensure full URL
                if not relative_link.startswith("http"):
                    full_link = self.base_url + relative_link
                else:
                    full_link = relative_link
                
                results.append({
                    "title": title,
                    "link": full_link
                })
                
            logger.info(f"✅ Successfully found {len(results)} links.")
            return results

        except Exception as e:
            logger.error(f"❌ Error fetching links: {e}")
            return []

    def fetch_content(self, url):
        """
        Step 2: Go to a specific announcement URL and get the text body.
        """
        try:
            response = requests.get(url, headers=self.headers, verify=False, timeout=15)
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Try standard content area
            content_div = soup.find("div", class_="field-name-body")
            
            # Fallback if structure varies
            if not content_div:
                content_div = soup.find("div", class_="region-content")
            
            if content_div:
                # Get clean text
                return content_div.get_text(separator="\n", strip=True)
            
            return ""
            
        except Exception as e:
            logger.error(f"❌ Error fetching content details ({url}): {e}")
            return ""