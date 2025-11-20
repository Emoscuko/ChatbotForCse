from __future__ import annotations
import os
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from .router import StrategyRouter

load_dotenv()

SHARED_SECRET  = os.getenv('SHARED_SECRET', 'hello')

class AskReq(BaseModel):
    text: str
    user: Optional[str] = None
    chat_id: Optional[str] = None
    is_group: Optional[bool] = None

class AskResp(BaseModel):
    answer: str

app = FastAPI(title='WhatsApp Strategy Bridge')
router = StrategyRouter()

@app.get('/health')
async def health():
    return { 'ok': True }

@app.post('/answer', response_model=AskResp)
async def answer(req: AskReq, x_auth: str = Header(default='')):
    if x_auth != SHARED_SECRET:
        raise HTTPException(status_code=401, detail='unauthorized')

    prompt = (req.text or '').strip()
    if not prompt:
        return { 'answer': 'Boş bir mesaj geldi. Bir cümle halinde sorunu yaz.' }

    out = await router.route(prompt, req.user, req.chat_id, bool(req.is_group))
    return { 'answer': out }