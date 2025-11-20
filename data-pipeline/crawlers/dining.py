"""
Dining Hall Menu Crawler
Scrapes menu data from university dining hall website.
"""

import logging
import requests
from datetime import datetime, date
from typing import Dict, Optional
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_menu(use_mock: bool = True) -> Optional[Dict]:
    """
    Fetch today's dining hall menu.
    
    Args:
        use_mock: If True, returns mock data for testing
        
    Returns:
        Dictionary containing menu data or None on failure
    """
    if use_mock:
        return _fetch_mock_menu()
    
    # Real scraping logic (to be implemented when site is accessible)
    url = os.getenv('DINING_URL', 'https://saglikkultur.akdeniz.edu.tr/tr/yemek-listesi')
    
    try:
        logger.info(f"Fetching menu from: {url}")
        
        response = requests.get(
            url,
            timeout=10,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # TODO: Implement actual scraping logic based on site structure
        # This is a placeholder that should be updated once site structure is known
        menu_data = _parse_menu_page(soup)
        
        if menu_data:
            logger.info("✅ Successfully fetched dining menu")
            return menu_data
        else:
            logger.warning("No menu data found, falling back to mock data")
            return _fetch_mock_menu()
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching menu: {e}")
        logger.info("Falling back to mock data")
        return _fetch_mock_menu()
    except Exception as e:
        logger.error(f"Unexpected error while fetching menu: {e}")
        logger.info("Falling back to mock data")
        return _fetch_mock_menu()


def _parse_menu_page(soup: BeautifulSoup) -> Optional[Dict]:
    """
    Parse menu from BeautifulSoup object.
    
    Args:
        soup: BeautifulSoup parsed HTML
        
    Returns:
        Dictionary with menu data
    """
    # TODO: Implement actual parsing logic
    # This is a placeholder - update based on actual site structure
    
    try:
        # Example parsing logic (update based on real site)
        menu_container = soup.find('div', class_='menu-content')
        
        if not menu_container:
            return None
        
        today = date.today().strftime('%Y-%m-%d')
        
        menu_data = {
            'date': today,
            'source': 'saglikkultur.akdeniz.edu.tr',
            'meals': {
                'lunch': [],
                'dinner': []
            }
        }
        
        # Add parsing logic here
        
        return menu_data
        
    except Exception as e:
        logger.error(f"Error parsing menu page: {e}")
        return None


def _fetch_mock_menu() -> Dict:
    """
    Return mock menu data for testing purposes.
    Simplified structure: Single date = Single list of items.
    
    Returns:
        Dictionary with mock menu data
    """
    today = date.today().strftime('%Y-%m-%d')
    
    # Realistic Turkish university dining menu samples (daily menu)
    daily_menus = [
        ['Mercimek Çorbası', 'Tavuk Sote', 'Bulgur Pilavı', 'Mevsim Salata', 'Ayran', 'Meyve'],
        ['Ezogelin Çorbası', 'Püreli Hasanpaşa Köfte', 'Bulgur Pilavı', 'Mevsim Salata', 'Revani'],
        ['Yayla Çorbası', 'Tavuk Döner', 'Patates Kızartması', 'Turşu', 'Ayran', 'Hoşaf'],
        ['Tarhana Çorbası', 'İzmir Köfte', 'Pirinç Pilavı', 'Cacık', 'Turşu', 'Meyve'],
        ['Domates Çorbası', 'Karışık Izgara', 'Kuru Fasulye', 'Pilav', 'Salata', 'Sütlaç'],
        ['Şehriye Çorbası', 'Fırın Tavuk', 'Makarna', 'Yoğurt', 'Ayran', 'Komposto'],
        ['Sebze Çorbası', 'Köri Soslu Tavuk', 'Pirinç Pilavı', 'Mevsim Salata', 'Kek']
    ]
    
    # Rotate menus based on day of week
    day_index = datetime.now().weekday()
    
    # SIMPLIFIED STRUCTURE: Just date and items
    menu_data = {
        'date': today,
        'items': daily_menus[day_index % len(daily_menus)],
        'source': 'mock_simple',
        'location': 'Akdeniz Üniversitesi Yemekhanesi'
    }
    
    logger.info(f"🍽️  Generated simple mock menu for {today}")
    return menu_data
