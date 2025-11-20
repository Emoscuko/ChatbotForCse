"""
Data Cleaning and Processing Module
Handles text cleaning and data normalization.
"""

import re
import logging
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize text data.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Convert to string if not already
    text = str(text)
    
    # Remove excessive whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove zero-width characters and other invisible unicode
    text = re.sub(r'[\u200b-\u200f\u202a-\u202e\ufeff]', '', text)
    
    return text


def clean_menu_data(menu_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean all text fields in menu data.
    
    Args:
        menu_data: Raw menu dictionary
        
    Returns:
        Cleaned menu dictionary
    """
    cleaned = {}
    
    for key, value in menu_data.items():
        if isinstance(value, str):
            cleaned[key] = clean_text(value)
        elif isinstance(value, dict):
            cleaned[key] = clean_menu_data(value)
        elif isinstance(value, list):
            cleaned[key] = [
                clean_text(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            cleaned[key] = value
    
    return cleaned


def clean_announcement(announcement: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean announcement data.
    
    Args:
        announcement: Raw announcement dictionary
        
    Returns:
        Cleaned announcement dictionary
    """
    cleaned = {}
    
    # Clean text fields
    for field in ['title', 'content', 'summary']:
        if field in announcement:
            cleaned[field] = clean_text(announcement[field])
    
    # Keep other fields as-is
    for key, value in announcement.items():
        if key not in cleaned:
            cleaned[key] = value
    
    return cleaned


def normalize_date(date_str: str) -> Optional[str]:
    """
    Normalize date string to YYYY-MM-DD format.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Normalized date string or None if invalid
    """
    from datetime import datetime
    
    # Common date formats to try
    formats = [
        '%Y-%m-%d',
        '%d.%m.%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%d-%m-%Y'
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    logger.warning(f"Could not parse date: {date_str}")
    return None


def validate_menu_data(menu_data: Dict[str, Any]) -> bool:
    """
    Validate menu data structure.
    
    Args:
        menu_data: Menu dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['date']
    
    for field in required_fields:
        if field not in menu_data:
            logger.error(f"Missing required field in menu data: {field}")
            return False
    
    return True


def validate_announcement(announcement: Dict[str, Any]) -> bool:
    """
    Validate announcement data structure.
    
    Args:
        announcement: Announcement dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['title', 'url']
    
    for field in required_fields:
        if field not in announcement:
            logger.error(f"Missing required field in announcement: {field}")
            return False
    
    return True
