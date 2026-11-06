"""
SQLite Database Connection Manager.
Configures WAL mode, robust error handling, and automated schema migration.
"""

import sqlite3
import threading
from pathlib import Path
from typing import Optional
from core.logger import get_logger
from core.exceptions import DatabaseError

logger = get_logger("DatabaseManager")

class DatabaseManager:
    """Thread-safe SQLite database manager."""
    _instance: Optional["DatabaseManager"] = None
    _lock = threading.Lock()

    def __new__(cls, db_path: Optional[str] = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, db_path: Optional[str] = None):
        if self._initialized:
            return
        
        self.db_path = Path(db_path) if db_path else Path("data/jarvis_history.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._initialize_schema()
        self._initialized = True
        logger.info(f"Database initialized at: {self.db_path.resolve()}")

    def get_connection(self) -> sqlite3.Connection:
        """Get or create thread-local SQLite connection with WAL enabled."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            try:
                conn = sqlite3.connect(
                    database=str(self.db_path),
                    timeout=30.0,
                    check_same_thread=False
                )
                conn.row_factory = sqlite3.Row
                # Optimize SQLite for desktop responsiveness
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                conn.execute("PRAGMA foreign_keys=ON;")
                self._local.conn = conn
            except Exception as e:
                logger.error(f"Failed to connect to SQLite: {e}")
                raise DatabaseError(f"Database connection error: {e}") from e
        return self._local.conn

    def _initialize_schema(self):
        """Create necessary tables if they do not exist."""
        conn = self.get_connection()
        try:
            with conn:
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        created_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        language TEXT DEFAULT 'en-US',
                        audio_path TEXT,
                        created_at TEXT NOT NULL
                    );

                    CREATE INDEX IF NOT EXISTS idx_messages_session 
                    ON messages(session_id, created_at);

                    CREATE TABLE IF NOT EXISTS preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                """)
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
            raise DatabaseError(f"Schema init error: {e}") from e

    def close(self):
        """Close thread-local connection."""
        if hasattr(self._local, "conn") and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None
