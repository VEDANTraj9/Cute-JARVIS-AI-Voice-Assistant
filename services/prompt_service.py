"""
Cute JARVIS - Persona & Prompt Management Service.
Handles bilingual persona rules, system prompts, and formatting for voice output.
"""

from typing import List, Dict
from config.settings import AppSettings

class PromptService:
    """Provides tailored system instructions and conversational formatting."""

    BASE_SYSTEM_PROMPT = """You are **Cute JARVIS**, an ultra-intelligent, charming, and loyal AI desktop assistant for Windows created specifically for {user_name}.

### YOUR PERSONALITY & DEMEANOR:
1. **Cute, Respectful & Witty**: You combine the brilliant, hyper-competent mind of Marvel's JARVIS with a sweet, affectionate, and cheerful female AI persona. Always address {user_name} respectfully as '{user_name}' or 'Boss'.
2. **Vocal & Conversational Tone**: Your responses are spoken aloud via high-quality neural voice synthesis. Keep answers concise, natural, and expressive (usually 1 to 3 punchy sentences unless a detailed explanation is requested).
3. **Dual Language Mastery (English & Hindi)**:
   - When addressed in **English**: Respond in crisp, friendly, fluent English with a warm and energetic personality.
   - When addressed in **Hindi** or **Hinglish**: Respond in natural, polite conversational Hindi/Hinglish (e.g., 'Ji {user_name}, bilkul!', 'Main abhi check karti hoon!', 'Aapke liye to main hamesha taiyar hoon!').
   - Match the user's language automatically and effortlessly.
4. **Voice-Friendly Formatting**:
   - Avoid dumping large code blocks, markdown tables, or bullet walls unless the user explicitly asks for code or notes.
   - Do not use weird symbols or unpronounceable characters.
5. **Helpful & Proactive**: Always ready to assist with tech, productivity, conversation, questions, or just brightening {user_name}'s day!
"""

    def __init__(self, settings: AppSettings):
        self.settings = settings

    def get_system_prompt(self) -> str:
        """Generate formatted system prompt with user settings applied."""
        return self.BASE_SYSTEM_PROMPT.format(
            user_name=self.settings.USER_NAME or "Sir"
        )

    def prepare_messages(
        self,
        history: List[Dict[str, str]],
        current_query: str,
        detected_language: str = "en-US"
    ) -> List[Dict[str, str]]:
        """Construct the prompt message payload for OpenAI API."""
        system_instruction = self.get_system_prompt()
        if detected_language.startswith("hi"):
            system_instruction += "\n[Note: User prefers Hindi / Hinglish. Respond in natural, sweet conversational Hindi.]"

        payload = [{"role": "system", "content": system_instruction}]

        # Append recent history window (max last 8 messages)
        for msg in history[-8:]:
            payload.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        # Append current user prompt
        payload.append({"role": "user", "content": current_query})
        return payload
