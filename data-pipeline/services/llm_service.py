import os
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load env explicitly for the script
load_dotenv()

logger = logging.getLogger(__name__)

class PipelineLLM:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing in .env")
            
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash" # Keep model consistent manually

    def generate_summary(self, text: str) -> str:
        """
        Synchronous call - Simple and robust for scripts.
        """
        if not text:
            return ""

        prompt = f"""
        System: You are a university assistant. Summarize this for students in 1 sentence.
        User: {text[:3000]}
        """

        try:
            # No 'await', no 'asyncio', just a direct call
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Pipeline LLM Error: {e}")
            return "Summary unavailable."