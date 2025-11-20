# backend/app/models/schemas.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    source: Optional[str] = None  # e.g., 'dining', 'announcement', 'ai'


class Announcement(BaseModel):
    title: str
    content: str
    source: str  # e.g., 'teams' or 'cse_website'
    url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DiningMenu(BaseModel):
    date: str  # Format YYYY-MM-DD
    soup: str
    main_dish: str
    side_dish: str
