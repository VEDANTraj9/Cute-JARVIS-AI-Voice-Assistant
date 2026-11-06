"""
Cute JARVIS AI Desktop Assistant - Application Entry Point.
Initializes runtime services, sets up High-DPI Qt display, and starts the event loop.
"""

import sys
import os
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config.settings import get_settings
from core.logger import get_logger
from storage.database import DatabaseManager
from storage.repository import ConversationRepository
from services.stt_service import STTService
from services.llm_service import LLMService
from services.tts_service import TTSService
from services.audio_player import AudioPlayer
from ui.main_window import MainWindow

logger = get_logger("Bootloader")

def main():
    """Bootstrap and launch Cute JARVIS."""
    logger.info("Initializing Cute JARVIS AI Assistant runtime...")

    # Configure High-DPI support for Windows 10/11 displays
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Cute JARVIS")
    app.setOrganizationName("CuteJARVIS")

    try:
        # Load configuration
        settings = get_settings()

        # Storage & Persistence Layer
        db_manager = DatabaseManager(settings.DATABASE_PATH)
        repository = ConversationRepository(db_manager)

        # Service Layer
        stt_service = STTService(settings)
        llm_service = LLMService(settings)
        tts_service = TTSService(settings)
        audio_player = AudioPlayer()

        # Main Window
        window = MainWindow(
            settings=settings,
            stt_service=stt_service,
            llm_service=llm_service,
            tts_service=tts_service,
            audio_player=audio_player,
            repository=repository
        )
        window.show()

        logger.info("Cute JARVIS Desktop GUI launched successfully.")
        sys.exit(app.exec())

    except Exception as e:
        logger.critical(f"Fatal application startup error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
