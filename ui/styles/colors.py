"""
UI Palette & Color System for Cute JARVIS.
Features dark navy, deep purple, glowing cyan, and cute neon pink accents.
"""

class Palette:
    """Color palette constants."""
    # Backgrounds
    BG_BASE = "#0A0D18"         # Deepest cosmic navy
    BG_SURFACE = "#101426"      # Primary container navy
    BG_SURFACE_LIGHT = "#161C36"# Raised card / elevated item
    BG_INPUT = "#131830"        # Text box & control field
    BG_HOVER = "#1D2446"        # Hover state highlight
    
    # Glowing Accents
    CYAN = "#00F0FF"            # Primary electric cyan accent
    CYAN_LIGHT = "#6EFAFF"      # Light cyan highlight
    CYAN_DIM = "#00828A"        # Muted cyan
    CYAN_GLOW = "rgba(0, 240, 255, 0.25)"
    
    PURPLE = "#8A4DFF"          # Futuristic neon violet purple
    PURPLE_LIGHT = "#B388FF"    # Pastel lavender highlight
    PURPLE_DIM = "#4A2699"      # Deep purple shadow
    PURPLE_GLOW = "rgba(138, 77, 255, 0.25)"
    
    PINK = "#FF5CA8"            # Cute anime neon pink
    PINK_LIGHT = "#FFA5D4"      # Soft blush
    PINK_GLOW = "rgba(255, 92, 168, 0.25)"
    
    # State Colors
    STATE_IDLE = "#6C7A9C"      # Serene slate blue
    STATE_LISTENING = "#00F0FF" # Pulsing neon cyan
    STATE_THINKING = "#8A4DFF"  # Swirling purple
    STATE_SPEAKING = "#FF5CA8"  # Energetic cute pink
    STATE_ERROR = "#FF4565"     # Vivid warning red
    STATE_SUCCESS = "#00E676"   # Electric neon green
    
    # Typography
    TEXT_TITLE = "#FFFFFF"      # Pure white
    TEXT_PRIMARY = "#EDF2F7"    # Crisp light silver
    TEXT_SECONDARY = "#8FA0C2"  # Muted silver navy
    TEXT_MUTED = "#556285"      # Subtle placeholder
    TEXT_CYAN = "#00F0FF"       # Cyan highlight
    TEXT_PINK = "#FF5CA8"       # Pink highlight
    
    # Borders & Dividers
    BORDER_DEFAULT = "#1E2748"  # Subtle separator
    BORDER_FOCUSED = "#00F0FF"  # Active glow border
    BORDER_PURPLE = "#3F2975"   # Purple accent border
