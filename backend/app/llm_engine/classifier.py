# backend/app/llm_engine/classifier.py

from typing import List, Tuple
from thefuzz import process

DINING_KEYWORDS: List[str] = [
    "yemek",
    "menü",
    "çorba",
    "karnım aç",
    "bugün ne var",
    "yemekhane",
    "aciktim",
]

ANNOUNCEMENT_KEYWORDS: List[str] = [
    "staj",
    "duyuru",
    "sınav",
    "büt",
    "ders",
    "hoca",
    "iptal",
    "program",
]


def _best_match(message: str, keywords: List[str]) -> Tuple[str, int]:
    """
    Returns (matched_keyword, score) using fuzzy matching.
    """
    match, score = process.extractOne(message, keywords)
    return match, score


def decide_intent(message: str) -> str:
    """
    Determines intent based on fuzzy keyword matching against predefined categories.
    
    Args:
        message: The user's message/query.
    
    Returns: 
        'dining', 'announcement', or 'general'.
    """
    if not message:
        return "general"

    # Dining intent score
    _, dining_score = _best_match(message, DINING_KEYWORDS)

    # Announcement intent score
    _, announcement_score = _best_match(message, ANNOUNCEMENT_KEYWORDS)

    # Threshold: score must be > 80 to classify
    threshold = 80

    if dining_score > threshold and dining_score >= announcement_score:
        return "dining"

    if announcement_score > threshold and announcement_score > dining_score:
        return "announcement"

    return "general"
