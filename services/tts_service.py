"""
Edge-TTS Speech Synthesis Service.
Generates cute, high-quality neural voices asynchronously with intelligent audio caching.
"""

import asyncio
import hashlib
import re
from pathlib import Path
from typing import Optional
import edge_tts

from config.constants import AUDIO_CACHE_DIR, VOICE_CATALOG
from config.settings import AppSettings
from core.logger import get_logger
from core.exceptions import TTSSynthesisError

logger = get_logger("TTSService")

class TTSService:
    """Handles text-to-speech generation using Microsoft Edge Neural Voices."""

    def __init__(self, settings: AppSettings):
        self.settings = settings
        AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _clean_text_for_speech(self, text: str) -> str:
        """Strip markdown markers, code blocks, and weird characters for smooth vocal output."""
        # Remove markdown code blocks
        clean = re.sub(r"```[\s\S]*?```", " [code snippet omitted] ", text)
        # Remove inline code backticks
        clean = re.sub(r"`([^`]+)`", r"\1", clean)
        # Remove URLs
        clean = re.sub(r"https?://\S+", " link ", clean)
        # Remove bold / italics
        clean = re.sub(r"[*_~]{1,3}", "", clean)
        # Remove markdown headers (#, ##)
        clean = re.sub(r"^#+\s*", "", clean, flags=re.MULTILINE)
        # Collapse extra spaces
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    def _get_cache_path(self, text: str, voice: str, pitch: str, rate: str) -> Path:
        """Generate deterministic cache file path based on synthesis parameters."""
        raw_key = f"{voice}:{pitch}:{rate}:{text}"
        digest = hashlib.md5(raw_key.encode("utf-8")).hexdigest()
        return AUDIO_CACHE_DIR / f"tts_{digest}.mp3"

    async def _synthesize_async(self, text: str, voice: str, pitch: str, rate: str, output_path: Path):
        """Perform async communication with Edge-TTS."""
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            pitch=pitch,
            rate=rate
        )
        await communicate.save(str(output_path))

    def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        pitch: Optional[str] = None,
        rate: Optional[str] = None,
        force_regenerate: bool = False
    ) -> Path:
        """
        Synthesize speech from text and return path to the MP3 file.
        Uses cached audio if already generated.
        """
        cleaned_text = self._clean_text_for_speech(text)
        if not cleaned_text:
            raise TTSSynthesisError("Cannot synthesize empty text.")

        active_voice = voice or self.settings.get_active_voice()
        active_pitch = pitch or self.settings.VOICE_PITCH
        active_rate = rate or self.settings.VOICE_RATE

        cached_file = self._get_cache_path(cleaned_text, active_voice, active_pitch, active_rate)

        # Return cached audio if present and not forced to regenerate
        if not force_regenerate and cached_file.exists() and cached_file.stat().st_size > 500:
            logger.debug(f"Audio cache hit: {cached_file.name}")
            return cached_file

        try:
            logger.info(f"Synthesizing speech with voice '{active_voice}' for: '{cleaned_text[:40]}...'")
            
            # Execute async synthesis in a fresh or existing loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Running in existing event loop
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run,
                            self._synthesize_async(cleaned_text, active_voice, active_pitch, active_rate, cached_file)
                        )
                        future.result(timeout=15.0)
                else:
                    loop.run_until_complete(
                        self._synthesize_async(cleaned_text, active_voice, active_pitch, active_rate, cached_file)
                    )
            except RuntimeError:
                asyncio.run(
                    self._synthesize_async(cleaned_text, active_voice, active_pitch, active_rate, cached_file)
                )

            if not cached_file.exists() or cached_file.stat().st_size < 500:
                raise TTSSynthesisError("Generated TTS audio file is empty or corrupted.")

            logger.info(f"Speech synthesis successful: {cached_file.name} ({cached_file.stat().st_size} bytes)")
            return cached_file

        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            raise TTSSynthesisError(f"TTS synthesis failed: {e}") from e
