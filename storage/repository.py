"""
Database Repository Layer.
Handles CRUD operations for conversation messages and user preferences.
"""

from typing import List, Optional
from datetime import datetime
from core.logger import get_logger
from core.exceptions import DatabaseError
from .database import DatabaseManager
from .models import ChatMessage

logger = get_logger("Repository")

class ConversationRepository:
    """Repository for managing conversation history and preferences."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def add_message(self, message: ChatMessage) -> int:
        """Insert a new chat message and return its generated ID."""
        conn = self.db.get_connection()
        try:
            with conn:
                cursor = conn.execute(
                    """
                    INSERT INTO messages (session_id, role, content, language, audio_path, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        message.session_id,
                        message.role,
                        message.content,
                        message.language,
                        message.audio_path,
                        message.created_at or datetime.now().isoformat()
                    )
                )
                message.id = cursor.lastrowid
                return message.id
        except Exception as e:
            logger.error(f"Failed to insert message: {e}")
            raise DatabaseError(f"Insert message failed: {e}") from e

    def get_recent_messages(self, session_id: str = "default", limit: int = 50) -> List[ChatMessage]:
        """Fetch the most recent conversation messages for a session."""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, session_id, role, content, language, audio_path, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit)
            )
            rows = cursor.fetchall()
            messages = [
                ChatMessage(
                    id=row["id"],
                    session_id=row["session_id"],
                    role=row["role"],
                    content=row["content"],
                    language=row["language"],
                    audio_path=row["audio_path"],
                    created_at=row["created_at"]
                )
                for row in reversed(rows)
            ]
            return messages
        except Exception as e:
            logger.error(f"Failed to retrieve messages: {e}")
            raise DatabaseError(f"Get messages failed: {e}") from e

    def clear_session(self, session_id: str = "default") -> bool:
        """Delete all messages for a given session."""
        conn = self.db.get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            return True
        except Exception as e:
            logger.error(f"Failed to clear session {session_id}: {e}")
            raise DatabaseError(f"Clear session failed: {e}") from e

    def set_preference(self, key: str, value: str):
        """Upsert a user preference key-value pair."""
        conn = self.db.get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO preferences (key, value, updated_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET
                        value = excluded.value,
                        updated_at = excluded.updated_at
                    """,
                    (key, value, datetime.now().isoformat())
                )
        except Exception as e:
            logger.error(f"Failed to set preference {key}: {e}")
            raise DatabaseError(f"Set preference failed: {e}") from e

    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve a stored user preference."""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute("SELECT value FROM preferences WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default
        except Exception as e:
            logger.error(f"Failed to get preference {key}: {e}")
            return default
