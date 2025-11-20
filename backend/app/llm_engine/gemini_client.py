# backend/app/llm_engine/gemini_client.py

import asyncio
import functools
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from google import genai

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize client with API key
client = genai.Client(api_key=settings.GEMINI_API_KEY)

MODEL_NAME = "gemini-2.5-flash"

# Thread pool for running sync API calls
_executor: Optional[ThreadPoolExecutor] = None


def _get_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=4)
    return _executor


def _call_model_sync(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text
    except Exception as e:
        logger.error(f"Error calling Gemini: {e}")
        raise


async def _run_in_threadpool(prompt: str) -> str:
    loop = asyncio.get_running_loop()
    executor = _get_executor()
    return await loop.run_in_executor(
        executor,
        functools.partial(_call_model_sync, prompt),
    )


async def generate_response(
    system_instruction: str,
    user_query: str,
    context_data: Optional[str] = None,
) -> str:
    context_data = context_data or ""
    
    prompt_parts = [
        f"System instruction:\n{system_instruction}",
        "",
        f"Context data:\n{context_data if context_data else 'N/A'}",
        "",
        f"User query:\n{user_query}",
    ]
    prompt = "\n".join(prompt_parts)

    try:
        response = await _run_in_threadpool(prompt)
        logger.info(f"Successfully generated response from {MODEL_NAME}")
        return response
    except Exception as e:
        logger.error(f"Error: {e}")
        return "Üzgünüm, şu anda yanıt üretemiyorum."
