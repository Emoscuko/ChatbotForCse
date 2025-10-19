import os
from dotenv import load_dotenv
load_dotenv()

from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
GEMINI_API_KEY = "AIzaSyCLsDh8xRawKdy30W3sWDxorgyuxnhksb4"
GEMINI_MODEL   = "gemini-2.0-flash"
SHARED_SECRET  = os.getenv("SHARED_SECRET", "hello")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY missing in environment")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    GEMINI_MODEL,
    system_instruction=(
        "Make your answers more romantic, flirty" \
        " Use Turkish language."
    ),
)

class AskReq(BaseModel):
    text: str
    user: Optional[str] = None
    chat_id: Optional[str] = None
    is_group: Optional[bool] = None

class AskResp(BaseModel):
    answer: str

app = FastAPI(title="WhatsApp AI Bridge")

@app.get("/health")
def health():
    return {"ok": True, "model": GEMINI_MODEL}

@app.post("/answer", response_model=AskResp)
def answer(req: AskReq, x_auth: str = Header(default="")):
    # --- Authentication temporarily disabled ---
    # if x_auth != SHARED_SECRET:
    #     raise HTTPException(status_code=401, detail="unauthorized")

    prompt = req.text.strip()
    if not prompt:
        return {"answer": "Boş bir mesaj geldi. Bir cümle halinde sorunu yaz."}

    try:
        resp = model.generate_content(
            prompt,
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ],
            generation_config={"temperature": 0.6, "max_output_tokens": 512},
        )
        text = (resp.text or "").strip()
        if not text:
            text = "Cevap üretemedim. Mesajını biraz daha açık yazar mısın?"
        return {"answer": text}
    except Exception as e:
        print("❌ Gemini error:", repr(e))
        return {"answer": "Şu an yanıt veremiyorum. Lütfen tekrar dener misin?"}
