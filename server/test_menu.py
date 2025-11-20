"""
Yemek menüsü görsel analiz fonksiyonunu test etmek için basit script
"""
import asyncio
import os
from datetime import date
from clients.akdeniz import get_menu_for

async def main():
    # OpenAI API key'i ayarla (eğer henüz ayarlanmamışsa)
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY environment variable bulunamadı!")
        print("Lütfen şu komutu çalıştırın:")
        print('$env:OPENAI_API_KEY="your-api-key-here"')
        return
    
    # Bugünün menüsünü al
    today = date.today()
    print(f"📅 {today.strftime('%d.%m.%Y')} için yemek menüsü çekiliyor...\n")
    
    menu = await get_menu_for(today)
    
    print("=" * 60)
    print(f"🍽️  {menu['date']}")
    print("=" * 60)
    
    if 'error' in menu:
        print(f"❌ Hata: {menu['error']}")
    else:
        for item in menu['items']:
            print(f"  • {item}")
    
    print("=" * 60)
    
    if 'raw_response' in menu:
        print("\n📝 OpenAI Raw Response:")
        print(menu['raw_response'])

if __name__ == '__main__':
    asyncio.run(main())
