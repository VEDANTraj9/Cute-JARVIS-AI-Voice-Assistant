"""
Text Interaction Worker Thread.
Handles manual text queries from the input box without blocking the PySide6 GUI thread.
"""

from typing import Optional
from PySide6.QtCore import QThread, Signal

from config.constants import AssistantState
from config.settings import AppSettings
from core.logger import get_logger
from services.llm_service import LLMService
from services.tts_service import TTSService
from services.audio_player import AudioPlayer
from storage.repository import ConversationRepository
from storage.models import ChatMessage

logger = get_logger("TextWorker")

class TextWorker(QThread):
    """Executes LLM inference and TTS speech generation for typed user queries."""

    state_changed = Signal(str)                   # AssistantState
    status_text = Signal(str)                     # Progress description
    audio_level = Signal(float)                   # 0.0 to 1.0
    user_message_ready = Signal(str, str)         # (text, language)
    assistant_reply_ready = Signal(str, str, str) # (text, language, audio_path)
    error_occurred = Signal(str, str)
    finished_cycle = Signal()

    def __init__(
        self,
        query: str,
        settings: AppSettings,
        llm_service: LLMService,
        tts_service: TTSService,
        audio_player: AudioPlayer,
        repository: ConversationRepository,
        parent=None
    ):
        super().__init__(parent)
        self.query = query.strip()
        self.settings = settings
        self.llm_service = llm_service
        self.tts_service = tts_service
        self.audio_player = audio_player
        self.repository = repository
        self._is_aborted = False

    def abort(self):
        self._is_aborted = True
        self.audio_player.stop()

    def run(self):
        if not self.query:
            self.finished_cycle.emit()
            return

        try:
            detected_lang = self.llm_service.detect_language(self.query)

            # Persist and signal user query
            self.user_message_ready.emit(self.query, detected_lang)
            try:
                self.repository.add_message(
                    ChatMessage(
                        role="user",
                        content=self.query,
                        language=detected_lang
                    )
                )
            except Exception as db_err:
                logger.error(f"Failed to persist user message: {db_err}")

            # Thinking / LLM
            self.state_changed.emit(AssistantState.THINKING.value)
            self.status_text.emit("Thinking & generating response...")

            recent_msgs = self.repository.get_recent_messages(limit=6)
            history_payload = [
                {"role": m.role, "content": m.content}
                for m in recent_msgs[:-1]
            ]

            reply_text = self.llm_service.generate_response(
                query=self.query,
                history=history_payload,
                language=detected_lang
            )

            if self._is_aborted:
                return

            # Speech Synthesis
            self.state_changed.emit(AssistantState.SPEAKING.value)
            self.status_text.emit("Voicing response...")

            active_voice = (
                self.settings.HINDI_VOICE
                if detected_lang.startswith("hi")
                else self.settings.ENGLISH_VOICE
            )

            audio_file = None
            try:
                audio_file = self.tts_service.synthesize(
                    text=reply_text,
                    voice=active_voice,
                    pitch=self.settings.VOICE_PITCH,
                    rate=self.settings.VOICE_RATE
                )
            except Exception as tts_err:
                logger.warning(f"TTS synthesis error: {tts_err}")

            self.assistant_reply_ready.emit(
                reply_text,
                detected_lang,
                str(audio_file) if audio_file else ""
            )

            try:
                self.repository.add_message(
                    ChatMessage(
                        role="assistant",
                        content=reply_text,
                        language=detected_lang,
                        audio_path=str(audio_file) if audio_file else None
                    )
                )
            except Exception as db_err:
                logger.error(f"Failed to persist assistant reply: {db_err}")

            # Audio Playback
            if audio_file and not self._is_aborted:
                playback_done = [False]

                def _on_done():
                    playback_done[0] = True

                def _on_lvl(lvl: float):
                    self.audio_level.emit(lvl)

                self.audio_player.play_audio(
                    audio_path=audio_file,
                    on_finished=_on_done,
                    on_level=_on_lvl
                )

                while not playback_done[0] and not self._is_aborted:
                    self.msleep(50)

        except Exception as e:
            logger.error(f"Error in TextWorker: {e}", exc_info=True)
            self.error_occurred.emit("Query Error", str(e))
        finally:
            self.state_changed.emit(AssistantState.IDLE.value)
            self.status_text.emit("Ready for command.")
            self.audio_level.emit(0.0)
            self.finished_cycle.emit()
