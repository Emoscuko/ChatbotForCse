import os
import logging
import json
import io
from PIL import Image  # Required for handling images
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
        self.model_name = "gemini-2.5-flash"

    def generate_summary(self, text: str) -> str:
        """
        Synchronous text-to-text summary.
        """
        if not text:
            return ""

        prompt = f"""
        System: You are a university assistant. Summarize this for students in 1 sentence.
        User: {text[:3000]}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Pipeline LLM Error: {e}")
            return "Summary unavailable."

    def extract_menu_from_image(self, image_bytes: bytes) -> list:
        """
        Takes raw image bytes, sends to Gemini Vision, returns a list of dicts (JSON).
        """
        if not image_bytes:
            return []

        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))

            prompt = """
            Analyze this image of a weekly dining menu.
            Extract the menu items for each day into a strict JSON format.
            
            Return a LIST of objects. Each object must have these keys:
            - "date": String (Format: YYYY-MM-DD). If year is missing, assume current year.
            - "day": String (e.g., "Pazartesi", "Salı")
            - "soup": String (The soup of the day)
            - "main_dish": String (The main course)
            - "side_dish": String (Rice, pasta, etc.)
            - "other": String (Dessert, yogurt, fruit, etc.)
            - "calories": Integer (Only if visible numbers like '850 cal' exist, otherwise null)

            IMPORTANT: 
            1. Return ONLY the raw JSON string. Do not use markdown code blocks (```json).
            2. If a day is not readable, skip it.
            """

            # Send Text + Image to Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, image]
            )
            
            # Clean up response just in case
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            
            # Parse to Python List
            menu_data = json.loads(clean_json)
            return menu_data

        except json.JSONDecodeError:
            logger.error("❌ LLM returned invalid JSON.")
            return []
        except Exception as e:
            logger.error(f"❌ LLM Vision Error: {e}")
            return []