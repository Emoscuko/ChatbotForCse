# Yemek Menüsü Görsel Analiz Sistemi

Bu sistem Akdeniz Üniversitesi yemek menüsü görselini analiz ederek günlük yemekleri ve kalorilerini çıkarır.

## 🎯 Özellikler

- Haftalık yemek menüsü görselini otomatik olarak bulur ve indirir
- OpenAI GPT-4 Vision API ile görseli analiz eder
- Belirtilen güne ait yemekleri ve kalorilerini listeler
- Türkçe dil desteği
- Strategy Design Pattern ile entegre

## 📋 Gereksinimler

### Python Paketleri
```bash
pip install -r requirements.txt
```

Yeni eklenen paketler:
- `pillow` - Görsel işleme
- `pytesseract` - OCR (opsiyonel, alternatif çözüm için)
- `openai` - OpenAI API client

### OpenAI API Key

OpenAI API kullanımı için bir API key gereklidir:

1. [OpenAI Platform](https://platform.openai.com/) hesabı oluşturun
2. API key alın
3. Environment variable olarak ayarlayın:

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

Veya `.env` dosyasına ekleyin:
```
OPENAI_API_KEY=sk-your-api-key-here
```

## 🚀 Kullanım

### Test Script ile

```bash
cd server
python test_menu.py
```

Bu script bugünün yemek menüsünü çekip gösterecektir.

### Ana Uygulama İçinde

Mevcut chatbot sisteminiz zaten `DiningMenuStrategy` kullanıyor. Sistem otomatik olarak yeni kodu kullanacak:

```python
from datetime import date
from clients.akdeniz import get_menu_for

# Bugünün menüsü
menu = await get_menu_for(date.today())
print(menu['date'])
for item in menu['items']:
    print(f"  - {item}")
```

## 🔄 Alternatif: OCR (Ücretsiz)

Eğer OpenAI API kullanmak istemezseniz, Tesseract OCR tabanlı alternatif de mevcuttur:

### Tesseract Kurulumu

**Windows:**
1. [Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki) indir
2. Kur (örn: `C:\Program Files\Tesseract-OCR`)
3. `akdeniz_ocr.py` içinde path'i ayarla

**Linux:**
```bash
sudo apt install tesseract-ocr tesseract-ocr-tur
```

### OCR Kullanımı

`clients/akdeniz.py` dosyasında şu değişikliği yapın:

```python
# OpenAI yerine OCR kullan
from .akdeniz_ocr import analyze_menu_image_with_ocr

# analyze_menu_image_with_openai yerine:
result = await analyze_menu_image_with_ocr(image_bytes, d)
```

**Not:** OCR doğruluğu Vision API'ye göre daha düşük olabilir.

## 📊 Örnek Çıktı

```
====================================================
🍽️  20 Kasım 2025 Çarşamba
====================================================
  • YEMEK: Mercimek Çorbası - 120 kcal
  • YEMEK: Tavuk Sote - 350 kcal
  • YEMEK: Makarna - 280 kcal
  • YEMEK: Pilav - 200 kcal
  • YEMEK: Çoban Salata - 80 kcal
====================================================
```

## 🏗️ Mimari

```
clients/
  akdeniz.py          # Ana modül (OpenAI Vision ile)
  akdeniz_ocr.py      # Alternatif modül (Tesseract OCR ile)
  
strategies/
  dining_menu.py      # Strategy pattern implementasyonu
  
test_menu.py          # Test script
```

## 🔧 Nasıl Çalışır?

1. **Sayfa Tarama:** `https://sks.akdeniz.edu.tr/tr/haftalik_yemek_listesi-6391` sayfasından menü görseli URL'i çıkarılır
2. **Görsel İndirme:** Menü görseli indirilir
3. **AI Analizi:** OpenAI GPT-4 Vision API ile görsel analiz edilir
4. **Parse:** Belirtilen gün için yemekler ve kaloriler parse edilir
5. **Sonuç:** Formatlanmış menü bilgisi döndürülür

## ⚠️ Notlar

- OpenAI API kullanımı ücretlidir (çok düşük, ~$0.01 per request)
- Görsel formatı değişirse kod güncellemesi gerekebilir
- OCR alternatifi ücretsiz ama daha az doğru
- Hafta sonu menüsü olmayabilir

## 🐛 Sorun Giderme

### "OPENAI_API_KEY bulunamadı"
Environment variable'ı doğru ayarlayın veya `.env` dosyası kullanın.

### "Menü görseli bulunamadı"
Web sitesinin yapısı değişmiş olabilir. `extract_image_url_from_page()` fonksiyonunu kontrol edin.

### "OCR hatası"
Tesseract'ın doğru kurulu olduğundan ve path'in ayarlı olduğundan emin olun.

## 📝 Geliştirme Fikirleri

- [ ] Haftalık tüm menüyü bir kerede çek
- [ ] Kalori toplamlarını hesapla
- [ ] Besin değerleri analizi
- [ ] Favori yemek bildirimleri
- [ ] Görsel önbellekleme (caching)
