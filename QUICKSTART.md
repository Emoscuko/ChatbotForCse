# 🍽️ Yemek Menüsü Görsel Analiz Sistemi - Hızlı Başlangıç

## ✅ Yapılan Değişiklikler

### 1. Güncellenen Dosyalar
- ✏️ `server/requirements.txt` - Yeni paketler eklendi (pillow, pytesseract, openai)
- ✏️ `server/clients/akdeniz.py` - Görsel analiz fonksiyonları eklendi
- ➕ `server/clients/akdeniz_ocr.py` - OCR alternatifi (opsiyonel)
- ➕ `server/test_menu.py` - Test script
- ➕ `MENU_ANALYSIS_README.md` - Detaylı dokümantasyon

### 2. Yeni Özellikler
✨ Web sitesinden yemek menüsü görselini otomatik bulma
✨ OpenAI GPT-4 Vision ile görsel analizi
✨ Günlük yemekleri ve kalorilerini çıkarma
✨ Türkçe dil desteği
✨ OCR alternatifi (ücretsiz ama daha az doğru)

## 🚀 Hızlı Kurulum

### 1. Paketleri Yükle
```powershell
cd server
pip install -r requirements.txt
```

### 2. OpenAI API Key Ayarla
```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

OpenAI API key almak için: https://platform.openai.com/

### 3. Test Et
```powershell
python test_menu.py
```

## 📝 Örnek Kullanım

```python
from datetime import date
from clients.akdeniz import get_menu_for

# Bugünün menüsünü al
menu = await get_menu_for(date.today())

# Çıktı:
# {
#   'date': '20 Kasım 2025 Çarşamba',
#   'items': [
#     'YEMEK: Mercimek Çorbası - 120 kcal',
#     'YEMEK: Tavuk Sote - 350 kcal',
#     'YEMEK: Pilav - 200 kcal',
#     ...
#   ]
# }
```

## 🔄 Sistem Nasıl Çalışır?

```
1. Web Sitesi → Görsel URL bulunur
           ↓
2. Görsel İndirilir (JPG)
           ↓
3. OpenAI Vision API → Analiz
           ↓
4. Parse → Yemekler + Kaloriler
           ↓
5. Sonuç → Chatbot'a
```

## 💰 Maliyet

- **OpenAI GPT-4o Vision:** ~$0.005-0.01 per request
- **Alternatif (OCR):** Ücretsiz (ama daha az doğru)

## ⚡ Performans

- Görsel indirme: ~1-2 saniye
- OpenAI analiz: ~3-5 saniye
- **Toplam:** ~5-7 saniye

## 🆘 Sorun Giderme

| Sorun | Çözüm |
|-------|-------|
| "OPENAI_API_KEY bulunamadı" | Environment variable ayarlayın |
| "Menü görseli bulunamadı" | Web sitesi yapısı değişmiş, `extract_image_url_from_page()` kontrol edin |
| "OpenAI API hatası" | API key geçerli mi? Kredi var mı kontrol edin |

## 📞 İletişim & Destek

Detaylı dokümantasyon için: `MENU_ANALYSIS_README.md`

## 🎯 Sonraki Adımlar

1. ✅ Paketleri yükle
2. ✅ API key ayarla  
3. ✅ Test et
4. 🚀 Ana uygulamada kullan

Mevcut `DiningMenuStrategy` otomatik olarak yeni kodu kullanacak!
