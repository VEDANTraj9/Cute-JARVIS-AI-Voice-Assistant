"""
Application Settings & Configuration Loader.
Uses pydantic-settings to cleanly parse environment variables and provide typed defaults.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import BASE_DIR, DEFAULT_DB_PATH

class AppSettings(BaseSettings):
    """Strongly typed application configuration."""
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # OpenAI API Configuration
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API secret key")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", description="OpenAI Chat Model")
    OPENAI_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0)
    OPENAI_MAX_TOKENS: int = Field(default=350, ge=50, le=4096)

    # Voice & Speech Synthesis (Edge-TTS)
    DEFAULT_LANGUAGE: str = Field(default="en-US", description="en-US or hi-IN")
    ENGLISH_VOICE: str = Field(default="en-US-AnaNeural", description="Cute English female voice")
    HINDI_VOICE: str = Field(default="hi-IN-SwaraNeural", description="Cute Hindi female voice")
    VOICE_RATE: str = Field(default="+0%", description="Speech playback rate (+- percentage)")
    VOICE_PITCH: str = Field(default="+5Hz", description="Speech pitch (+- Hz or st)")
    VOICE_VOLUME: str = Field(default="+0%", description="Speech volume (+- percentage)")

    # Assistant Persona
    ASSISTANT_NAME: str = Field(default="JARVIS", description="AI Name")
    USER_NAME: str = Field(default="Sir", description="User preferred title")
    ASSISTANT_PERSONALITY: str = Field(default="cute_loyal", description="Persona preset")

    # Microphone & Audio Settings
    MIC_ENERGY_THRESHOLD: int = Field(default=300, description="Audio energy threshold for silence")
    DYNAMIC_ENERGY_THRESHOLD: bool = Field(default=True, description="Auto-adjust for ambient room noise")
    MIC_PHRASE_TIME_LIMIT: int = Field(default=12, description="Max recording duration in seconds")
    MIC_PAUSE_THRESHOLD: float = Field(default=1.0, description="Silence threshold before speech is processed")

    # Storage & System
    APP_THEME: str = Field(default="dark", description="Visual theme (dark)")
    LOG_LEVEL: str = Field(default="INFO", description="Log verbosity")
    DATABASE_PATH: str = Field(default=str(DEFAULT_DB_PATH), description="SQLite DB Path")

    def get_active_voice(self) -> str:
        """Return active TTS voice identifier based on currently selected language."""
        if self.DEFAULT_LANGUAGE.startswith("hi"):
            return self.HINDI_VOICE
        return self.ENGLISH_VOICE

    def update_setting(self, key: str, value: any):
        """Update a setting in-memory."""
        if hasattr(self, key):
            setattr(self, key, value)

@lru_cache()
def get_settings() -> AppSettings:
    """Return cached AppSettings singleton."""
    return AppSettings()
