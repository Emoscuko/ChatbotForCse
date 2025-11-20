# 📂 Akdeniz CSE Assistant - Project Architecture

Bu doküman, projenin dosya yapısını, her bir dosyanın ne işe yaradığını ve sorumluluk alanlarını içerir.

**Teknoloji Yığını:**
* **Client:** React Native (Expo Router)
* **Backend:** Python FastAPI ve Gemini API
* **Database:** MongoDB (Motor Async Driver)
* **Data Pipeline:** Python Scripts 

---

## 🌳 Root Directory (Kök Dizin)

Tüm projenin barındığı ana klasör.

```text
akdeniz-cse-assistant/
├── .gitignore               # Git'e yüklenmemesi gerekenler (node_modules, venv, .env vb.)
├── README.md                # Proje kurulum ve kullanım kılavuzu
├── docker-compose.yml       # Local geliştirme için MongoDB ve Redis'i ayağa kaldıran dosya
├── backend/                 # [Backend Ekibi] API ve AI Core
├── data-pipeline/           # [Data Ekibi] Scraper ve Cronjoblar
└── mobile-app/              # [Client Ekibi] Mobil Uygulama

backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py      # POST /chat -> Kullanıcı sohbet endpoint'i. LLM Agent'ı burada çağrılır.
│   │   │   ├── feed.py      # GET /feed -> Duyurular akışını (Teams+Site) JSON olarak döner.
│   │   │   └── webhooks.py  # POST /webhook/teams -> Teams'ten gelen mesajları dinler.
│   │   └── deps.py          # Veritabanı bağlantısını (Session) dependency injection ile dağıtır.
│   │
│   ├── core/
│   │   ├── config.py        # .env dosyasını okur (MONGO_URL, OPENAI_API_KEY).
│   │   └── security.py      # API Key kontrolü veya basit JWT işlemleri (Opsiyonel).
│   │
│   ├── db/
│   │   ├── client.py        # MongoDB bağlantısını (Motor Client) başlatan dosya.
│   │   └── collections.py   # Koleksiyon isimlerini sabit olarak tutar (örn: DB_COLLECTION_MSG = "messages")
│   │
│   ├── models/              # Pydantic Modelleri (Veri Doğrulama ve Şema)
│   │   ├── chat.py          # ChatMessage (role, content) şeması.
│   │   ├── feed.py          # Announcement (title, source, date) şeması. Teams ve Site ortaktır.
│   │   └── menu.py          # DiningMenu (soup, main_dish) şeması.
│   │
│   ├── llm_engine/          # AI Mantık Katmanı
│   │   ├── agent.py         # Router Logic. Gelen sorunun türüne göre hangi Tool'u seçeceğine karar verir.
│   │   ├── prompts.py       # System Promptları ("Sen Akdeniz Cse asistanısın...").
│   │   └── tools/           # LLM'in kullanacağı yetenekler
│   │       ├── nosql_search.py  # MongoDB'de $text araması yapan fonksiyon.
│   │       └── menu_lookup.py   # O günün yemeğini veritabanından çeken fonksiyon.
│   │
│   └── main.py              # FastAPI uygulamasını başlatan giriş noktası (App Entry Point).
│
├── .env                     # Backend özelindeki gizli anahtarlar.
├── Dockerfile               # Azure'a deploy ederken kullanılacak imaj dosyası.
└── requirements.txt         # python-dotenv, fastapi, uvicorn, motor, openai, langchain

---

data-pipeline/
├── crawlers/                # Ham veriyi çeken botlar
│   ├── base.py              # Ortak scraper ayarları (User-Agent headerları vb.)
│   ├── cse_site.py          # Akdeniz CSE duyurularını parse eder (BeautifulSoup).
│   └── dining.py            # Yemekhane listesini çeker.
│
├── processors/              # Veri temizleme işçileri
│   ├── text_cleaner.py      # HTML tagleri siler, gereksiz boşlukları atar (\n\t temizliği).
│   └── normalizer.py        # Tarih formatlarını standart hale getirir (ISO 8601).
│
├── storage/                 # Veritabanı Yazma Katmanı
│   └── mongo_writer.py      # Veriyi "Upsert" eder. (URL veya ID varsa güncelle, yoksa ekle).
│
├── jobs/                    # Zamanlanmış Görevlerin (Cronjob) çalıştırıcısı
│   ├── sync_feed.py         # [30 DK'da bir] cse_site.py çalıştırır -> mongo_writer'a gönderir.
│   ├── sync_menu.py         # [Her sabah 08:00] dining.py çalıştırır -> mongo_writer'a gönderir.
│   └── process_legacy.py    # [Tek seferlik] Eski WhatsApp loglarını temizleyip DB'ye atar.
│
├── .env                     # Pipeline özelindeki veritabanı şifreleri.
└── requirements.txt         # beautifulsoup4, requests, pymongo, python-dotenv

---

mobile-app/
├── app/                     # Expo Router (Dosya tabanlı navigasyon)
│   ├── (tabs)/              # Alt Tab Menüsü (Bottom Navigation)
│   │   ├── index.tsx        # [Chat Ekranı] Ana sayfa. Sohbet arayüzü.
│   │   ├── feed.tsx         # [Duyurular Ekranı] Teams ve Site duyuruları burada listelenir.
│   │   └── settings.tsx     # Profil ve ayarlar.
│   │
│   ├── _layout.tsx          # Tüm sayfaları kapsayan ana şablon (Theme Provider vb.)
│   └── +not-found.tsx       # 404 sayfası.
│
├── src/
│   ├── components/          # Tekrar kullanılabilir UI parçaları
│   │   ├── Bubble.tsx       # Chat mesaj balonu (User/Bot ayrımı stili).
│   │   ├── FeedCard.tsx     # Duyuru kartı (Başlık, Tarih, Kaynak ikonu).
│   │   └── InputBox.tsx     # Mesaj yazma alanı.
│   │
│   ├── core/                # Uygulama genel ayarları
│   │   ├── theme.ts         # Renk paleti (Akdeniz mavisi vb.)
│   │   └── config.ts        # API URL'i (Development/Production ayrımı).
│   │
│   ├── services/            # Backend ile iletişim
│   │   ├── api.ts           # Axios instance (Base URL ayarlı).
│   │   ├── chatService.ts   # sendMessage() fonksiyonu.
│   │   └── feedService.ts   # getAnnouncements() fonksiyonu.
│   │
│   ├── types/               # TypeScript Arayüzleri (Backend'deki Pydantic modelleriyle uyumlu)
│   │   ├── IMessage.ts      # { id, text, sender, timestamp }
│   │   └── IAnnouncement.ts # { id, title, content, source, url }
│   │
│   └── utils/               # Yardımcı fonksiyonlar
│       └── date.ts          # "2 saat önce", "Bugün" gibi tarih formatlayıcılar.
│
├── assets/                  # Resimler, fontlar, logolar.
├── app.json                 # Expo ayarları (Paket ismi, versiyon, icon).
├── package.json             # React Native kütüphaneleri.
└── tsconfig.json            # TypeScript ayarları.