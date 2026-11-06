"""
Central Event Bus for Decoupled Qt Signal/Slot Communication.
Coordinates UI updates, worker threads, and speech pipeline events.
"""

from typing import Optional
from PySide6.QtCore import QObject, Signal

class JarvisEventBus(QObject):
    """Global Qt Signal dispatcher for thread-safe cross-component communication."""

    # State & Status Signals
    state_changed = Signal(str)                   # AssistantState (IDLE, LISTENING, etc.)
    status_text_changed = Signal(str)             # e.g., "Calibrating noise...", "Thinking..."
    audio_level_changed = Signal(float)           # 0.0 to 1.0 (Reactive waveform amplitude)
    
    # Message Pipeline Signals
    user_message_ready = Signal(str, str)         # (content, language)
    assistant_message_ready = Signal(str, str, str) # (content, language, audio_file_path)
    
    # Configuration & Control Signals
    language_changed = Signal(str)                # "en-US" or "hi-IN"
    voice_changed = Signal(str)                   # Voice ID
    mic_toggled = Signal(bool)                    # True = Active, False = Muted/Off
    playback_muted_toggled = Signal(bool)         # Audio mute state
    
    # Diagnostic & Error Signals
    error_raised = Signal(str, str)               # (title, message)
    connection_status_updated = Signal(str, bool, str) # (service, is_healthy, message)

_bus_instance: Optional[JarvisEventBus] = None

def get_event_bus() -> JarvisEventBus:
    """Return singleton event bus."""
    global _bus_instance
    if _bus_instance is None:
        _bus_instance = JarvisEventBus()
    return _bus_instance
