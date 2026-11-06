"""
Core Custom Application Exceptions.
"""

class JarvisException(Exception):
    """Base exception for all JARVIS errors."""
    pass

class AudioDeviceError(JarvisException):
    """Raised when microphone or audio output is unavailable."""
    pass

class SpeechRecognitionError(JarvisException):
    """Raised when audio capture or transcription fails."""
    pass

class SpeechTimeoutError(SpeechRecognitionError):
    """Raised when speech listener times out without capturing voice."""
    pass

class TTSSynthesisError(JarvisException):
    """Raised when Edge-TTS fails to synthesize speech audio."""
    pass

class LLMServiceError(JarvisException):
    """Raised when OpenAI API call fails or encounters invalid credentials."""
    pass

class DatabaseError(JarvisException):
    """Raised on SQLite storage or transaction failure."""
    pass
