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
                logger.warning(f"Failed to initialize GenAI client: {e}. Using deterministic engine.")

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

    def generate_chat_response(
        self,
        system_context: str,
        user_message: str,
        chat_history_formatted: List[Dict[str, str]]
    ) -> Optional[str]:
        """Generate conversational response using Gemini LLM if available."""
        if not self.client:
            return None

        try:
            contents = []
            # Add chat history context
            for msg in chat_history_formatted[-6:]: # Last 6 turns for context memory
                role = "user" if msg.get("sender") == "user" else "model"
                contents.append(f"{role.upper()}: {msg.get('content')}")
            
            contents.append(f"USER: {user_message}")

            prompt = f"SCENARIO STATE:\n{system_context}\n\nCONVERSATION:\n" + "\n".join(contents)
            
            system_instruction = (
                "You are the RESQ-AI Coordinator Agent, an authoritative, conversational disaster-response AI assistant. "
                "Answer the user's question directly and concisely based strictly on the current scenario state. "
                "Do NOT repeat the entire location and scenario summary unless explicitly asked. "
                "Understand contextual references (like 'that zone', 'why', 'there', 'blocked road', 'vehicles left'). "
                "Keep answers direct, professional, and natural. Do NOT invent facts outside the scenario."
            )

            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
                max_output_tokens=300
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logger.error(f"GenAI chat call failed: {e}.")
            return None
        return None

# Singleton instance
llm_service = LLMService()
