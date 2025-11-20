"""
CSE Department Announcements Crawler
Scrapes announcements from CSE department website.
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import random

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_announcements(use_mock: bool = True) -> List[Dict]:
    """
    Fetch announcements from CSE website.
    
    Args:
        use_mock: If True, returns mock data for testing
        
    Returns:
        List of announcement dictionaries
    """
    if use_mock:
        return _fetch_mock_announcements()
    
    # Real scraping logic
    url = os.getenv('CSE_ANNOUNCEMENTS_URL', 'https://cse.akdeniz.edu.tr/tr/duyurular')
    
    try:
        logger.info(f"Fetching announcements from: {url}")
        
        response = requests.get(
            url,
            timeout=10,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # TODO: Implement actual scraping logic
        announcements = _parse_announcements_page(soup)
        
        if announcements:
            logger.info(f"✅ Successfully fetched {len(announcements)} announcements")
            return announcements
        else:
            logger.warning("No announcements found, falling back to mock data")
            return _fetch_mock_announcements()
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching announcements: {e}")
        logger.info("Falling back to mock data")
        return _fetch_mock_announcements()
    except Exception as e:
        logger.error(f"Unexpected error while fetching announcements: {e}")
        logger.info("Falling back to mock data")
        return _fetch_mock_announcements()


def _parse_announcements_page(soup: BeautifulSoup) -> List[Dict]:
    """
    Parse announcements from BeautifulSoup object.
    
    Args:
        soup: BeautifulSoup parsed HTML
        
    Returns:
        List of announcement dictionaries
    """
    # TODO: Implement actual parsing logic
    announcements = []
    
    try:
        # Example parsing logic (update based on real site structure)
        announcement_items = soup.find_all('div', class_='announcement-item')
        
        for item in announcement_items:
            title_elem = item.find('h3') or item.find('a')
            content_elem = item.find('p') or item.find('div', class_='content')
            link_elem = item.find('a')
            date_elem = item.find('span', class_='date')
            
            if title_elem and link_elem:
                announcement = {
                    'title': title_elem.get_text(strip=True),
                    'url': link_elem.get('href'),
                    'content': content_elem.get_text(strip=True) if content_elem else '',
                    'source': 'cse_website',
                    'created_at': datetime.utcnow()
                }
                
                if date_elem:
                    announcement['publish_date'] = date_elem.get_text(strip=True)
                
                announcements.append(announcement)
        
        return announcements
        
    except Exception as e:
        logger.error(f"Error parsing announcements page: {e}")
        return []


def _fetch_mock_announcements() -> List[Dict]:
    """
    Return mock announcement data for testing.
    
    Returns:
        List of mock announcement dictionaries
    """
    # Realistic CSE announcement titles
    announcement_templates = [
        {
            'title': 'Bahar Dönemi Ders Programı Açıklandı',
            'content': '2024-2025 Bahar Dönemi ders programı açıklanmıştır. Öğrencilerimiz ders kayıtlarını belirtilen tarihler arasında yapabilirler.',
            'category': 'academic'
        },
        {
            'title': 'Yapay Zeka ve Makine Öğrenmesi Semineri',
            'content': 'Prof. Dr. Ahmet Yılmaz tarafından verilecek olan "Modern Yapay Zeka Uygulamaları" konulu seminer 15 Aralık tarihinde Amfi-1\'de gerçekleştirilecektir.',
            'category': 'event'
        },
        {
            'title': 'Bitirme Projesi Teslim Tarihleri',
            'content': 'Bitirme projesi ara rapor teslim tarihi 20 Aralık olarak belirlenmiştir. Öğrencilerin raporlarını zamanında teslim etmeleri gerekmektedir.',
            'category': 'deadline'
        },
        {
            'title': 'Staj Başvuruları Başladı',
            'content': 'Yaz dönemi staj başvuruları başlamıştır. Başvurular 30 Ocak tarihine kadar devam edecektir.',
            'category': 'internship'
        },
        {
            'title': 'ACM Öğrenci Kulübü Etkinliği',
            'content': 'ACM Öğrenci Kulübü tarafından düzenlenen Hackathon etkinliği 25-26 Aralık tarihlerinde gerçekleştirilecektir.',
            'category': 'club'
        },
        {
            'title': 'Vize Sınavı Tarihleri Güncellendi',
            'content': 'Vize sınavı tarihleri güncellenmiştir. Yeni sınav takvimi bölüm web sitesinde yayınlanmıştır.',
            'category': 'exam'
        },
        {
            'title': 'Mezuniyet Töreni Duyurusu',
            'content': '2024 yılı mezuniyet töreni 28 Haziran Cuma günü saat 14:00\'te yapılacaktır.',
            'category': 'graduation'
        },
        {
            'title': 'Yeni Laboratuvar Açıldı',
            'content': 'Bilgisayar Mühendisliği bölümünde Siber Güvenlik Laboratuvarı hizmete açılmıştır.',
            'category': 'facility'
        }
    ]
    
    # Generate 3-5 random announcements
    num_announcements = random.randint(3, 5)
    selected_templates = random.sample(announcement_templates, min(num_announcements, len(announcement_templates)))
    
    announcements = []
    
    for i, template in enumerate(selected_templates, 1):
        # Generate dates in the past week
        days_ago = random.randint(0, 7)
        created_date = datetime.utcnow() - timedelta(days=days_ago)
        
        announcement = {
            'title': template['title'],
            'content': template['content'],
            'url': f'https://cse.akdeniz.edu.tr/tr/duyuru/{random.randint(1000, 9999)}',
            'source': 'mock_data',
            'category': template['category'],
            'created_at': created_date,
            'publish_date': created_date.strftime('%d.%m.%Y')
        }
        
        announcements.append(announcement)
    
    logger.info(f"📰 Generated {len(announcements)} mock announcements")
    return announcements
