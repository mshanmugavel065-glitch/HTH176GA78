import json
import logging
from typing import Dict, Any, List, Optional
from config import settings

logger = logging.getLogger(__name__)

# Try importing google-genai
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class LLMService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.LLM_MODEL
        self.client = None
        
        if GENAI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Initialized Google GenAI Client successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize GenAI client: {e}. Falling back to demo mode.")

    def generate_json(self, prompt: str, system_instruction: str = "") -> Optional[Dict[str, Any]]:
        """Attempt LLM JSON generation, return None if fails or unconfigured."""
        if not self.client:
            return None
        
        try:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=system_instruction if system_instruction else "You are an emergency response AI agent. Always reply with valid JSON only."
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            if response and response.text:
                cleaned = response.text.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                return json.loads(cleaned.strip())
        except Exception as e:
            logger.error(f"GenAI call failed: {e}. Falling back to deterministic agent reasoning engine.")
            return None
        return None

# Singleton instance
llm_service = LLMService()
