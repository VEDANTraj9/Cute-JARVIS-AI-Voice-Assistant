"""
Voice Interaction Worker Thread.
Runs the Speech-to-Text -> LLM Inference -> Text-to-Speech -> Audio Playback pipeline
on an isolated QThread to prevent GUI freezing.
"""

from typing import Optional, List, Dict
from PySide6.QtCore import QThread, Signal

from config.constants import AssistantState
from config.settings import AppSettings
from core.logger import get_logger
from core.exceptions import (
    AudioDeviceError, SpeechRecognitionError,
    SpeechTimeoutError, TTSSynthesisError, LLMServiceError
)
from services.stt_service import STTService
from services.llm_service import LLMService
from services.tts_service import TTSService
from services.audio_player import AudioPlayer
from storage.repository import ConversationRepository
from storage.models import ChatMessage

logger = get_logger("VoiceWorker")

class VoiceWorker(QThread):
    """Asynchronous worker for capturing voice and executing the assistant pipeline."""

    state_changed = Signal(str)                   # AssistantState
    status_text = Signal(str)                     # Progress description
    audio_level = Signal(float)                   # RMS level (0.0 to 1.0)
    user_speech_ready = Signal(str, str)          # (transcription, language)
    assistant_reply_ready = Signal(str, str, str) # (text, language, audio_path)
    error_occurred = Signal(str, str)             # (title, message)
    finished_cycle = Signal()

    def __init__(
        self,
        settings: AppSettings,
        stt_service: STTService,
        llm_service: LLMService,
        tts_service: TTSService,
        audio_player: AudioPlayer,
        repository: ConversationRepository,
        parent=None
    ):
        super().__init__(parent)
        self.settings = settings
        self.stt_service = stt_service
        self.llm_service = llm_service
        self.tts_service = tts_service
        self.audio_player = audio_player
        self.repository = repository
        self._is_aborted = False

    def abort(self):
        """Signal thread to cancel current cycle."""
        self._is_aborted = True
        self.audio_player.stop()

    def run(self):
        """Execute the voice interaction cycle."""
        self._is_aborted = False
        lang = self.settings.DEFAULT_LANGUAGE

        try:
            # 1. Listen for voice
            self.state_changed.emit(AssistantState.LISTENING.value)
            self.status_text.emit("Listening to your voice... Speak now!")

            user_text = self.stt_service.listen_and_transcribe(language=lang)
            if self._is_aborted:
                return

            # Detect language (English vs Hindi/Hinglish)
            detected_lang = self.llm_service.detect_language(user_text)

            # Persist and signal user message
            self.user_speech_ready.emit(user_text, detected_lang)
            try:
                self.repository.add_message(
                    ChatMessage(
                        role="user",
                        content=user_text,
                        language=detected_lang
                    )
                )
            except Exception as db_err:
                logger.error(f"Failed to persist user message: {db_err}")

            # 2. Thinking / LLM Inference
            self.state_changed.emit(AssistantState.THINKING.value)
            self.status_text.emit("Thinking & generating intelligent response...")

            # Retrieve recent conversation context
            recent_msgs = self.repository.get_recent_messages(limit=6)
            history_payload = [
                {"role": m.role, "content": m.content}
                for m in recent_msgs[:-1]  # Exclude current message already stored
            ]

            reply_text = self.llm_service.generate_response(
                query=user_text,
                history=history_payload,
                language=detected_lang
            )

            if self._is_aborted:
                return

            # 3. Speech Synthesis (Edge-TTS)
            self.state_changed.emit(AssistantState.SPEAKING.value)
            self.status_text.emit("Synthesizing cute neural voice...")

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
                logger.warning(f"TTS Synthesis failed; continuing with text only: {tts_err}")

            # Persist and signal assistant reply
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

            # 4. Playback Audio
            if audio_file and not self._is_aborted:
                self.status_text.emit("Speaking...")
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

                # Wait for playback completion or abort
                while not playback_done[0] and not self._is_aborted:
                    self.msleep(50)

        except SpeechTimeoutError:
            logger.info("Voice worker timed out waiting for speech.")
            self.status_text.emit("No speech detected.")
        except AudioDeviceError as ade:
            logger.error(f"Microphone error in voice worker: {ade}")
            self.error_occurred.emit("Microphone Issue", str(ade))
        except SpeechRecognitionError as sre:
            logger.warning(f"Speech recognition error: {sre}")
            self.status_text.emit(str(sre))
        except Exception as e:
            logger.error(f"Unhandled exception in VoiceWorker: {e}", exc_info=True)
            self.error_occurred.emit("Voice Loop Error", str(e))
        finally:
            self.state_changed.emit(AssistantState.IDLE.value)
            self.status_text.emit("Ready for command.")
            self.audio_level.emit(0.0)
            self.finished_cycle.emit()
