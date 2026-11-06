"""
Speech-To-Text (STT) Recognition Service.
Captures microphone audio streams with ambient noise calibration and transcribes speech.
"""

from typing import Optional, Tuple
import speech_recognition as sr
from config.settings import AppSettings
from core.logger import get_logger
from core.exceptions import AudioDeviceError, SpeechRecognitionError, SpeechTimeoutError

logger = get_logger("STTService")

class STTService:
    """Handles microphone capture and dual-language speech recognition."""

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = settings.MIC_ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = settings.DYNAMIC_ENERGY_THRESHOLD
        self.recognizer.pause_threshold = settings.MIC_PAUSE_THRESHOLD
        self._is_calibrated = False

    def is_microphone_available(self) -> Tuple[bool, str]:
        """Check if any microphone input device is accessible."""
        try:
            device_names = sr.Microphone.list_microphone_names()
            if not device_names:
                return False, "No microphone input devices found."
            return True, f"Found {len(device_names)} audio input devices."
        except Exception as e:
            return False, f"Microphone check failed: {e}"

    def calibrate_noise(self, duration: float = 1.0):
        """Calibrate ambient room noise levels."""
        try:
            with sr.Microphone() as source:
                logger.info(f"Calibrating ambient noise ({duration}s)...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                self._is_calibrated = True
                logger.info(f"Calibrated noise threshold: {self.recognizer.energy_threshold:.1f}")
        except Exception as e:
            logger.warning(f"Could not calibrate ambient noise: {e}")

    def listen_and_transcribe(
        self,
        language: Optional[str] = None,
        timeout: Optional[int] = None,
        phrase_time_limit: Optional[int] = None
    ) -> str:
        """
        Listen to the microphone and transcribe spoken words into text.
        Returns recognized string.
        """
        lang = language or self.settings.DEFAULT_LANGUAGE
        stt_lang = "hi-IN" if lang.startswith("hi") else "en-IN"
        time_limit = phrase_time_limit or self.settings.MIC_PHRASE_TIME_LIMIT
        listen_timeout = timeout or 8

        try:
            with sr.Microphone() as source:
                if not self._is_calibrated:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                    self._is_calibrated = True

                logger.info(f"Listening for speech (Language: {stt_lang}, Timeout: {listen_timeout}s)...")
                audio_data = self.recognizer.listen(
                    source,
                    timeout=listen_timeout,
                    phrase_time_limit=time_limit
                )

        except sr.WaitTimeoutError as e:
            logger.debug("Speech recognition timed out (no speech detected).")
            raise SpeechTimeoutError("No speech detected within the timeout period.") from e
        except OSError as e:
            logger.error(f"Microphone hardware error: {e}")
            raise AudioDeviceError(f"Microphone access error: {e}") from e
        except Exception as e:
            logger.error(f"Error opening microphone: {e}")
            raise AudioDeviceError(f"Could not access microphone: {e}") from e

        # Transcribe captured audio via Google Speech Recognition API
        try:
            logger.info("Transcribing audio payload...")
            transcription = self.recognizer.recognize_google(audio_data, language=stt_lang)
            logger.info(f"Transcription successful: '{transcription}'")
            return transcription.strip()
        except sr.UnknownValueError:
            logger.info("Speech was unintelligible or silent.")
            raise SpeechRecognitionError("Could not understand the audio.")
        except sr.RequestError as e:
            logger.error(f"Speech recognition service unavailable: {e}")
            raise SpeechRecognitionError(f"Speech service error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {e}")
            raise SpeechRecognitionError(f"Transcription failure: {e}") from e
