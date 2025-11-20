"""
OpenAI kullanmadan, görselden OCR ile yemek menüsünü çıkaran alternatif fonksiyon.
Bu versiyon Tesseract OCR kullanır (ücretsiz).
"""
from __future__ import annotations
import re
from datetime import date
from typing import Optional
from PIL import Image
from io import BytesIO
import pytesseract

# Eğer Windows'ta Tesseract yüklüyse path'i belirtmeniz gerekebilir:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


async def analyze_menu_image_with_ocr(image_bytes: bytes, target_date: date) -> dict:
    """Tesseract OCR kullanarak menü görselini analiz eder (ücretsiz alternatif)."""
    try:
        # Görseli aç
        image = Image.open(BytesIO(image_bytes))
        
        # OCR ile metni çıkar
        text = pytesseract.image_to_string(image, lang='tur')
        
        day_names = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        target_day = day_names[target_date.weekday()]
        
        # Metni satırlara ayır
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Hedef günü bul
        day_index = -1
        for i, line in enumerate(lines):
            if target_day.lower() in line.lower():
                day_index = i
                break
        
        if day_index == -1:
            return {
                'date': f"{target_date.day} {['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'][target_date.month-1]} {target_date.year} {target_day}",
                'items': [f'({target_day} günü menüde bulunamadı)'],
                'raw_text': text
            }
        
        # Günün menü öğelerini topla (günün satırından sonraki 5-10 satır)
        menu_items = []
        for i in range(day_index + 1, min(day_index + 10, len(lines))):
            line = lines[i]
            # Eğer başka bir gün ismi gelirse dur
            if any(day.lower() in line.lower() for day in day_names):
                break
            # Kalori bilgisi içeren veya yemek ismi gibi görünen satırları ekle
            if re.search(r'\d+\s*(kcal|kalori)', line, re.IGNORECASE) or len(line) > 3:
                menu_items.append(line)
        
        return {
            'date': f"{target_date.day} {['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'][target_date.month-1]} {target_date.year} {target_day}",
            'items': menu_items if menu_items else ['(Menü öğeleri okunamadı)'],
            'raw_text': text
        }
        
    except Exception as e:
        return {
            'error': f'OCR hatası: {str(e)}'
        }


# NOT: Bu fonksiyonu kullanmak için clients/akdeniz.py içindeki
# analyze_menu_image_with_openai yerine analyze_menu_image_with_ocr'yi çağırmanız gerekir
