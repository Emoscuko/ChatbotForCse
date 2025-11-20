from __future__ import annotations
import os
import re
import httpx
from bs4 import BeautifulSoup
from datetime import date, datetime
from typing import Optional
import base64
from io import BytesIO
from PIL import Image

MENU_URL = os.getenv('AKDENIZ_MENU_URL', 'https://sks.akdeniz.edu.tr/tr/haftalik_yemek_listesi-6391')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

async def fetch_menu_html() -> str:
    """Yemek menüsü sayfasının HTML içeriğini çeker."""
    async with httpx.AsyncClient() as client:
        r = await client.get(MENU_URL, timeout=10)
        r.raise_for_status()
        return r.text

async def extract_image_url_from_page() -> Optional[str]:
    """Sayfadan yemek menüsü görselinin URL'sini çıkarır."""
    html = await fetch_menu_html()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Görseli bul - genellikle content div içinde img tag olarak bulunur
    img_tags = soup.find_all('img')
    for img in img_tags:
        src = img.get('src', '')
        # Yemek menüsü görseli genellikle 'yemekhane' veya 'Slayt' içerir
        if 'yemekhane' in src.lower() or 'slayt' in src.lower() or 'menu' in src.lower():
            # Relative URL'yi absolute'a çevir
            if src.startswith('/'):
                src = 'https://webis.akdeniz.edu.tr' + src
            elif not src.startswith('http'):
                src = 'https://webis.akdeniz.edu.tr/' + src
            return src
    
    # Eğer bulamazsa, doğrudan bilinen URL'yi dene
    return 'https://webis.akdeniz.edu.tr/uploads/1019/yemekhane/Slayt1%20copy%208eb61724-095d-4c99-b0d8-6461e877ffd3.JPG'


async def download_image(url: str) -> bytes:
    """Görseli indirir."""
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=15)
        r.raise_for_status()
        return r.content


async def analyze_menu_image_with_openai(image_bytes: bytes, target_date: date) -> dict:
    """OpenAI Vision API kullanarak menü görselini analiz eder."""
    if not OPENAI_API_KEY:
        return {
            'error': 'OpenAI API key bulunamadı. Lütfen OPENAI_API_KEY environment variable\'ını ayarlayın.'
        }
    
    # Görseli base64'e çevir
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    day_names = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
    target_day = day_names[target_date.weekday()]
    date_str = f"{target_date.day:02d}.{target_date.month:02d}.{target_date.year}"
    
    prompt = f"""Bu görselde haftalık yemek menüsü var. {target_day} ({date_str}) için:
1. Hangi yemekler var? (Çorba, Ana Yemek, Ek Yemek, Pilav, Salata vb.)
2. Her yemeğin kalorisi nedir?

Lütfen sadece {target_day} gününe ait bilgileri ver ve şu formatta yanıtla:
YEMEK: [yemek adı] - [kalori] kcal
Her satır bir yemek olsun."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {OPENAI_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4o',
                    'messages': [
                        {
                            'role': 'user',
                            'content': [
                                {'type': 'text', 'text': prompt},
                                {
                                    'type': 'image_url',
                                    'image_url': {
                                        'url': f'data:image/jpeg;base64,{base64_image}'
                                    }
                                }
                            ]
                        }
                    ],
                    'max_tokens': 500
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            content = result['choices'][0]['message']['content']
            
            # Yanıtı parse et
            items = []
            for line in content.split('\n'):
                line = line.strip()
                if line and ('kcal' in line.lower() or 'kalori' in line.lower()):
                    items.append(line)
            
            return {
                'date': f"{target_date.day} {['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'][target_date.month-1]} {target_date.year} {target_day}",
                'items': items if items else [content],
                'raw_response': content
            }
            
    except Exception as e:
        return {
            'error': f'OpenAI API hatası: {str(e)}'
        }


async def get_menu_for(d: date) -> dict:
    """Returns a dict like { 'date': '20 Ekim 2025 Pazartesi', 'items': ['Çorba - 150 kcal', ...] }
    Görsel analizi yaparak günlük yemek menüsünü ve kalorilerini döndürür.
    """
    try:
        # Görsel URL'sini al
        image_url = await extract_image_url_from_page()
        if not image_url:
            return {
                'date': f"{d.day} {['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'][d.month-1]} {d.year}",
                'items': ['(Menü görseli bulunamadı)']
            }
        
        # Görseli indir
        image_bytes = await download_image(image_url)
        
        # OpenAI ile analiz et
        result = await analyze_menu_image_with_openai(image_bytes, d)
        
        if 'error' in result:
            return {
                'date': f"{d.day} {['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'][d.month-1]} {d.year}",
                'items': [result['error']]
            }
        
        return result
        
    except Exception as e:
        return {
            'date': f"{d.day} {['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'][d.month-1]} {d.year}",
            'items': [f'(Hata oluştu: {str(e)})']
        }