from __future__ import annotations
import os
import httpx
from bs4 import BeautifulSoup
from datetime import date
from . import akdeniz_selectors as sel  # optional future extension

MENU_URL = os.getenv('AKDENIZ_MENU_URL', 'https://sks.akdeniz.edu.tr/tr/haftalik_yemek_listesi-6391')

async def fetch_menu_html() -> str:
    async with httpx.AsyncClient() as client:
        r = await client.get(MENU_URL, timeout=10)
        r.raise_for_status()
        return r.text

async def get_menu_for(d: date) -> dict:
    """Returns a dict like { 'date': '20 Ekim 2025 Pazartesi', 'items': ['Çorba', 'Ana yemek', ...] }
    Tries to be resilient to markup differences: looks for the row/block that mentions the date.
    """
    html = await fetch_menu_html()
    soup = BeautifulSoup(html, 'html.parser')

    # Heuristic 1: search any element whose text contains the day/month as Turkish words/numbers
    day = str(d.day)
    month_names = [
        'Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'
    ]
    month = month_names[d.month-1]

    # Find candidate containers (rows/cards) containing the date string
    candidates = [el for el in soup.find_all(text=True) if el and day in el and month in el]
    block = soup
    if candidates:
        block = candidates[0].parent
        # walk up a bit to get the container
        for _ in range(3):
            if block.parent:
                block = block.parent

    # Now pull list items or table cells from that block
    items = []
    for li in block.find_all('li'):
        t = li.get_text(strip=True)
        if t:
            items.append(t)
    if not items:
        # perhaps a table layout
        for td in block.find_all('td'):
            t = td.get_text(' ', strip=True)
            if t and not any(x in t for x in ['Tarih','Kalori']):
                items.append(t)

    items = [x for x in items if len(x) > 1][:10]  # bound length
    return {
        'date': f"{day} {month} {d.year}",
        'items': items or ['(Menü bulunamadı — sayfa yapısı değişmiş olabilir)']
    }