"""
Storage Data Models for SQLite database.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

@dataclass
class ChatMessage:
    """Represents a single conversational turn."""
    id: Optional[int] = None
    session_id: str = "default"
    role: str = "user"  # 'user' | 'assistant' | 'system'
    content: str = ""
    language: str = "en-US"
    audio_path: Optional[str] = None
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)

@dataclass
class UserPreference:
    """Represents saved user configuration."""
    key: str
    value: str
    updated_at: str = ""

    def __post_init__(self):
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
