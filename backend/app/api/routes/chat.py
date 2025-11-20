# backend/app/api/routes/chat.py

from datetime import datetime, date as date_type
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse
from app.llm_engine.classifier import decide_intent
from app.llm_engine.gemini_client import generate_response
from app.db.mongo import db

router = APIRouter(prefix="/chat", tags=["chat"])

SYSTEM_INSTRUCTION = (
    "You are a helpful assistant for Akdeniz University Computer Engineering students. "
    "Answer in Turkish. Be concise and friendly."
)


async def _fetch_dining_context() -> str:
    """
    Fetch today's dining menu from MongoDB.
    Simplified structure: Single list of items per day.
    
    Returns:
        Formatted dining menu string or a 'not found' message.
    """
    try:
        today = date_type.today().strftime("%Y-%m-%d")
        
        # --- DEBUG LOG BAŞLANGICI ---
        print(f"DEBUG: Aranan Tarih: {today}")
        print(f"DEBUG: Koleksiyon Adı: dining")
        # --- DEBUG LOG BİTİŞ ---
        
        menu = await db.db["dining"].find_one({"date": today})
        
        # --- DEBUG LOG SONUÇ ---
        print(f"DEBUG: Bulunan Menü: {menu}")
        # -----------------------
        
        if not menu:
            return f"VERİTABANI BİLGİSİ: {today} tarihi için yemek listesi bulunamadı."
        
        # Simplified structure: Just read the 'items' list
        items = menu.get('items', [])
        location = menu.get('location', 'Akdeniz Üniversitesi Yemekhanesi')
        
        if items:
            menu_str = ", ".join(items)
            context = f"VERİTABANI BİLGİSİ ({today} Menüsü - {location}): {menu_str}"
        else:
            context = "VERİTABANI BİLGİSİ: Menü kaydı var ama içi boş."
        
        return context
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return f"Error fetching dining menu: {str(e)}"


async def _fetch_announcements_context() -> str:
    """
    Fetch the 3 most recent announcements from MongoDB.
    
    Returns:
        Formatted announcements string or a 'not found' message.
    """
    try:
        announcements = await db.db["announcements"].find() \
            .sort("created_at", -1) \
            .limit(3) \
            .to_list(length=3)
        
        if not announcements:
            return "No recent announcements."
        
        context_lines = ["Recent Announcements:"]
        for i, ann in enumerate(announcements, 1):
            title = ann.get("title", "N/A")
            content = ann.get("content", "N/A")
            source = ann.get("source", "N/A")
            context_lines.append(
                f"{i}. [{source}] {title}\n   {content[:100]}..."
            )
        
        return "\n".join(context_lines)
    except Exception as e:
        return f"Error fetching announcements: {str(e)}"


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint that routes user messages to appropriate handlers.
    
    Flow:
    1. Determine intent from user message (dining, announcement, or general).
    2. Fetch relevant context from MongoDB based on intent.
    3. Call Gemini API with system instruction, context, and user query.
    4. Return the generated response with source attribution.
    
    Args:
        request: ChatRequest containing message and optional user_id.
    
    Returns:
        ChatResponse with reply and source.
    
    Raises:
        HTTPException: If database or API calls fail.
    """
    try:
        # Step 1: Determine intent
        intent = decide_intent(request.message)
        
        # Step 2: Fetch context based on intent
        if intent == "dining":
            context_data = await _fetch_dining_context()
        elif intent == "announcement":
            context_data = await _fetch_announcements_context()
        else:  # general
            context_data = "General conversation. Feel free to ask anything about Akdeniz University or Computer Engineering."
        
        # Step 3: Generate response from Gemini
        reply = await generate_response(
            system_instruction=SYSTEM_INSTRUCTION,
            user_query=request.message,
            context_data=context_data
        )
        
        # Step 4: Return response with source
        return ChatResponse(
            reply=reply,
            source=intent
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )
