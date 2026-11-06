"""
OpenAI LLM Integration Service.
Provides streaming responses, context memory, language detection,
and graceful offline fallback when no API key is configured.
"""

import re
from typing import List, Dict, Generator, Optional
from datetime import datetime

from openai import OpenAI, OpenAIError, AuthenticationError
from config.settings import AppSettings
from core.logger import get_logger
from core.exceptions import LLMServiceError
from .prompt_service import PromptService

logger = get_logger("LLMService")

class LLMService:
    """Manages conversational inference via OpenAI API with built-in fallbacks."""

    # Common Hinglish and Hindi markers
    HINDI_KEYWORDS = {
        "kya", "kaise", "kyun", "kab", "kahan", "mera", "meri", "mere",
        "tum", "aap", "kaun", "hai", "hain", "hoon", "hoga", "hogi",
        "batao", "karo", "kardo", "shukriya", "dhanyawad", "namaste",
        "kaise ho", "kya haal hai", "suno", "theek"
    }

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.prompt_service = PromptService(settings)
        self._client: Optional[OpenAI] = None
        self._init_client()

    def _init_client(self):
        """Initialize OpenAI client if API key is present."""
        api_key = self.settings.OPENAI_API_KEY.strip()
        if api_key and not api_key.startswith("your_openai_"):
            try:
                self._client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized with configured API key.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self._client = None
        else:
            logger.warning("No valid OPENAI_API_KEY found in configuration. Operating in fallback mode.")
            self._client = None

    def refresh_client(self, new_api_key: Optional[str] = None):
        """Reinitialize client when user updates API key in UI settings."""
        if new_api_key:
            self.settings.OPENAI_API_KEY = new_api_key.strip()
        self._init_client()

    def detect_language(self, text: str) -> str:
        """
        Detect whether the query is in Hindi / Hinglish or English.
        Returns 'hi-IN' or 'en-US'.
        """
        # Check Devanagari unicode range (U+0900 to U+097F)
        if re.search(r"[\u0900-\u097F]", text):
            return "hi-IN"

        # Check Hinglish token overlap
        words = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))
        matched = words.intersection(self.HINDI_KEYWORDS)
        if len(matched) >= 2 or (len(words) <= 3 and len(matched) >= 1):
            return "hi-IN"

        return self.settings.DEFAULT_LANGUAGE

    def is_configured(self) -> bool:
        """Check if active OpenAI client has valid credentials."""
        return self._client is not None

    def _fallback_response(self, query: str, language: str) -> str:
        """Provide charming offline responses when API key is missing or offline."""
        q_lower = query.lower().strip()
        user = self.settings.USER_NAME or "Sir"
        is_hindi = language.startswith("hi")

        # Time & Date queries
        if any(w in q_lower for w in ["time", "samay", "kitne baje"]):
            now_str = datetime.now().strftime("%I:%M %p")
            if is_hindi:
                return f"{user}, abhi waqt {now_str} ho raha hai!"
            return f"{user}, the current time is {now_str}."

        if any(w in q_lower for w in ["date", "din", "tareekh"]):
            today_str = datetime.now().strftime("%A, %B %d, %Y")
            if is_hindi:
                return f"{user}, aaj ki tareekh {today_str} hai!"
            return f"Today is {today_str}, {user}!"

        # Greetings
        if any(w in q_lower for w in ["hello", "hi", "hey", "namaste", "suno"]):
            if is_hindi:
                return f"Namaste {user}! Main aapki Cute JARVIS hoon. Kahiye, main aapki kya madad kar sakti hoon?"
            return f"Hello {user}! Cute JARVIS is online and ready for action. How can I assist you today?"

        # Identity
        if any(w in q_lower for w in ["who are you", "tum kaun ho", "tera naam"]):
            if is_hindi:
                return f"Main aapki Cute JARVIS hoon, {user}! Aapki personal smart assistant."
            return f"I am your Cute JARVIS AI Assistant, {user}! Built to make your desktop experience wonderful."

        # Default prompt to configure API key
        if is_hindi:
            return (
                f"{user}, main bilkul tayyar hoon! Lekin meri poori intelligence unlock karne ke liye, "
                "kripya Settings panel mein jaakar apna OpenAI API Key enter kar dijiye!"
            )
        return (
            f"I'm ready to help, {user}! To unleash my full AI intelligence, please enter your "
            "OpenAI API Key in the Settings panel or .env file."
        )

    def generate_response(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
        language: Optional[str] = None
    ) -> str:
        """Generate a complete text response to the user query."""
        detected_lang = language or self.detect_language(query)

        # Fallback if client is unconfigured
        if not self._client:
            logger.info("Using built-in persona fallback response.")
            return self._fallback_response(query, detected_lang)

        try:
            messages = self.prompt_service.prepare_messages(
                history=history or [],
                current_query=query,
                detected_language=detected_lang
            )

            logger.info(f"Calling OpenAI model: {self.settings.OPENAI_MODEL}...")
            response = self._client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=messages,
                temperature=self.settings.OPENAI_TEMPERATURE,
                max_tokens=self.settings.OPENAI_MAX_TOKENS
            )

            content = response.choices[0].message.content
            if not content:
                return self._fallback_response(query, detected_lang)

            return content.strip()

        except AuthenticationError as e:
            logger.error(f"OpenAI Authentication error: {e}")
            return (
                f"Sir, your OpenAI API key seems to be invalid. Please check your key in the Settings tab."
            )
        except OpenAIError as e:
            logger.warning(f"OpenAI API connection/service issue ({e}). Gracefully switching to persona fallback.")
            return self._fallback_response(query, detected_lang)
        except Exception as e:
            logger.error(f"Unexpected error in LLM generation: {e}")
            return self._fallback_response(query, detected_lang)
