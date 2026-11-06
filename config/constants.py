"""
Cute JARVIS - Application Constants and Configuration Types.
Defines UI palettes, voice mappings, assistant statuses, and system defaults.
"""

from enum import Enum
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
AUDIO_CACHE_DIR = CACHE_DIR / "audio"
LOGS_DIR = BASE_DIR / "logs"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Default Database Path
DEFAULT_DB_PATH = DATA_DIR / "jarvis_history.db"

# Assistant Operational States
class AssistantState(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"
    ERROR = "ERROR"

# Supported Languages
class SupportedLanguage(str, Enum):
    ENGLISH = "en-US"
    HINDI = "hi-IN"

# Edge-TTS Cute Voice Catalog
VOICE_CATALOG = {
    "en-US": [
        {"id": "en-US-AnaNeural", "name": "Ana (Cute & Cheerful)", "gender": "Female", "style": "Cute"},
        {"id": "en-US-JennyNeural", "name": "Jenny (Warm & Natural)", "gender": "Female", "style": "Friendly"},
        {"id": "en-US-AvaNeural", "name": "Ava (Modern & Crisp)", "gender": "Female", "style": "Futuristic"},
        {"id": "en-US-AriaNeural", "name": "Aria (Playful & Expressive)", "gender": "Female", "style": "Expressive"},
    ],
    "hi-IN": [
        {"id": "hi-IN-SwaraNeural", "name": "Swara (Sweet & Melodic)", "gender": "Female", "style": "Cute"},
        {"id": "hi-IN-MadhurNeural", "name": "Madhur (Polite & Gentle)", "gender": "Male", "style": "Gentle"},
    ]
}

# Theme Colors: Dark Navy, Rich Purple, Glowing Cyan & Pink Accents
THEME_COLORS = {
    # Backgrounds
    "bg_primary": "#0A0D18",      # Ultra dark navy base
    "bg_secondary": "#11162B",    # Card/Panel navy
    "bg_tertiary": "#1A203C",     # Input/Hover container
    "bg_glass": "rgba(17, 22, 43, 0.75)", # Frosted glass overlay
    
    # Accent Colors
    "accent_cyan": "#00F0FF",     # Glowing electric cyan
    "accent_cyan_glow": "rgba(0, 240, 255, 0.35)",
    "accent_purple": "#8A4DFF",   # Neon violet purple
    "accent_purple_glow": "rgba(138, 77, 255, 0.35)",
    "accent_pink": "#FF5CA8",     # Cute soft anime pink
    "accent_pink_glow": "rgba(255, 92, 168, 0.35)",
    
    # State Colors
    "status_idle": "#6C7A9C",     # Soft steel blue
    "status_listening": "#00F0FF",# Neon cyan pulse
    "status_thinking": "#8A4DFF", # Purple energy
    "status_speaking": "#FF5CA8", # Cute pink wave
    "status_error": "#FF4466",    # Vivid red
    
    # Text
    "text_primary": "#F2F5FF",    # Crisp white-silver
    "text_secondary": "#95A1C6",  # Muted silver-blue
    "text_muted": "#5A6588",      # Low-emphasis text
    "text_accent": "#00F0FF",     # Cyan highlight text
    
    # Borders
    "border_subtle": "#1E2648",   # Subtle container line
    "border_glow": "#2C396B",     # Active border
}
