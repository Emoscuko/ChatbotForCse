from __future__ import annotations
import os
from .base import Strategy, StrategyContext

# Optional: smalltalk via Gemini as graceful fallback
USE_LLM = os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')

class FallbackStrategy(Strategy):
    name = 'fallback'

    async def handle(self, ctx: StrategyContext, intent: dict) -> str:
        if not USE_LLM:
            return 'Tam anlayamadım. Örnek: "Yarın Algoritma dersi var mı?" veya "Bugünkü yemekhane menüsü nedir?"'
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            model = genai.GenerativeModel(os.getenv('GEMINI_MODEL', 'gemini-2.0-flash'))
            resp = model.generate_content(
                f"Kısa ve net Türkçe yanıtla: {ctx.text}",
                generation_config={"temperature": 0.2, "max_output_tokens": 256},
            )
            return (resp.text or 'Cevap üretemedim.').strip()
        except Exception:
            return 'Sorunu netleştiremedim. Biraz daha açık yazar mısın?'