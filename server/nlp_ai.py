# server/nlp_ai.py
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

async def detect_intent_ai(text: str) -> dict:
    prompt = f"""
Mesaj: "{text}"
Aşağıdakilerden hangisine ait olduğunu belirle:
1. teams_announcements → Teams dersi veya duyuru soruları
2. dining_menu → Yemekhane / yemek menüsü soruları
3. moderation → Küfür, argo, kural ihlali mesajları
4. fallback → Diğer her şey
Sadece strateji adını döndür.
"""
    resp = model.generate_content(prompt, generation_config={"temperature": 0})
    name = (resp.text or "fallback").strip().split()[0].lower()
    return {"name": name}
