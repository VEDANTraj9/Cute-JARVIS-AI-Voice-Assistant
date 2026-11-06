"""
Audio Playback Service.
Plays synthesized speech with pygame.mixer and manages playback events,
muting, volume control, and audio level callbacks for visualization.
"""

import threading
import time
from pathlib import Path
from typing import Optional, Callable
from core.logger import get_logger

logger = get_logger("AudioPlayer")

class AudioPlayer:
    """Manages audio playback and audio level notifications for UI reactive animations."""

    def __init__(self):
        self._is_initialized = False
        self._is_playing = False
        self._is_muted = False
        self._volume = 1.0
        self._on_playback_finished: Optional[Callable[[], None]] = None
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._init_pygame()

    def _init_pygame(self):
        """Initialize pygame mixer safely."""
        try:
            import pygame
            if not pygame.mixer.get_init():
                # Low buffer size for minimal audio latency
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._is_initialized = True
            logger.info("Pygame audio mixer initialized successfully.")
        except Exception as e:
            logger.warning(f"Could not initialize Pygame mixer: {e}")
            self._is_initialized = False

    def is_playing(self) -> bool:
        """Check if audio is currently actively playing."""
        if not self._is_initialized:
            return False
        import pygame
        return pygame.mixer.music.get_busy()

    def set_muted(self, muted: bool):
        """Toggle audio mute."""
        self._is_muted = muted
        if self._is_initialized:
            import pygame
            pygame.mixer.music.set_volume(0.0 if muted else self._volume)
        logger.info(f"Audio muted state set to: {muted}")

    def set_volume(self, volume: float):
        """Set playback volume between 0.0 and 1.0."""
        self._volume = max(0.0, min(1.0, volume))
        if self._is_initialized and not self._is_muted:
            import pygame
            pygame.mixer.music.set_volume(self._volume)

    def stop(self):
        """Immediately stop currently playing audio."""
        self._stop_event.set()
        if self._is_initialized:
            try:
                import pygame
                pygame.mixer.music.stop()
            except Exception as e:
                logger.error(f"Error stopping audio: {e}")
        self._is_playing = False

    def play_audio(
        self,
        audio_path: Path,
        on_finished: Optional[Callable[[], None]] = None,
        on_level: Optional[Callable[[float], None]] = None
    ):
        """
        Play audio file asynchronously and invoke callbacks.
        """
        if not audio_path.exists():
            logger.error(f"Audio file not found: {audio_path}")
            if on_finished:
                on_finished()
            return

        self.stop()
        self._stop_event.clear()
        self._on_playback_finished = on_finished

        def _play_worker():
            try:
                if not self._is_initialized:
                    self._init_pygame()
                
                import pygame
                pygame.mixer.music.load(str(audio_path))
                pygame.mixer.music.set_volume(0.0 if self._is_muted else self._volume)
                pygame.mixer.music.play()
                self._is_playing = True

                # Monitor playback loop
                while pygame.mixer.music.get_busy() and not self._stop_event.is_set():
                    # Generate subtle simulated RMS pulse amplitude for waveform visualization
                    if on_level:
                        import math
                        t = time.time() * 10
                        pseudo_amp = 0.4 + 0.5 * abs(math.sin(t) * math.cos(t * 1.5))
                        on_level(pseudo_amp)
                    time.sleep(0.05)

                if on_level:
                    on_level(0.0)

            except Exception as e:
                logger.error(f"Audio playback error: {e}")
            finally:
                self._is_playing = False
                if self._on_playback_finished and not self._stop_event.is_set():
                    try:
                        self._on_playback_finished()
                    except Exception as cb_err:
                        logger.error(f"Error in on_finished callback: {cb_err}")

        self._playback_thread = threading.Thread(target=_play_worker, daemon=True)
        self._playback_thread.start()
