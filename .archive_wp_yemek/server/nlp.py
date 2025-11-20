from __future__ import annotations
import re
from typing import Optional
from .utils.dates import today_ist, tomorrow_ist

# Very lightweight intent detector for Turkish

COURSE_PATTERN = re.compile(r"\b(algoritma|algorithm|veri yap[ıi]lar[ıi]|game programming|matematik|physics)\b", re.I)

DINING_PAT = re.compile(r"\b(yemekhane|yemek|men[üu]|menusu|menüsü|program[ıi])\b", re.I)
TODAY_PAT = re.compile(r"\b(bug[üu]n|bugunki|bugünkü)\b", re.I)
TOMORROW_PAT = re.compile(r"\b(yar[ıi]n|yarin)\b", re.I)
CLASS_PAT = re.compile(r"\b(dersi|dersi\s*var\s*m[ıi]|ders|lab|s[ıi]nav)\b", re.I)


def detect_intent(text: str) -> dict:
    t = (text or '').strip()
    if not t:
        return { 'name': 'none' }

    # Dining hall
    if DINING_PAT.search(t):
        rel = 'today'
        if TOMORROW_PAT.search(t):
            rel = 'tomorrow'
        return { 'name': 'dining_menu', 'date_rel': rel }

    # Class/Teams check
    if CLASS_PAT.search(t) or TOMORROW_PAT.search(t):
        m = COURSE_PATTERN.search(t)
        course = (m.group(1) if m else None)
        d = tomorrow_ist() if TOMORROW_PAT.search(t) else None
        return { 'name': 'teams_announcements', 'course': course, 'date': d }

    return { 'name': 'fallback' }