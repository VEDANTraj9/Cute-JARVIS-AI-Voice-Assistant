"""
Master Dashboard Window for Cute JARVIS.
Assembles the futuristic desktop interface, animated avatar visualizer,
conversation panel, bottom control bar, worker threads, and event handling.
"""

from typing import Optional
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QFrame, QMessageBox
)

from config.constants import AssistantState
from config.settings import AppSettings
from core.logger import get_logger
from services.stt_service import STTService
from services.llm_service import LLMService
from services.tts_service import TTSService
from services.audio_player import AudioPlayer
from storage.repository import ConversationRepository
from ui.styles.colors import Palette
from ui.styles.qss_templates import get_application_stylesheet
from ui.components import (
    AvatarWaveformWidget,
    StatusBarWidget,
    ControlBarWidget,
    ConversationPanel,
    SettingsDialog
)
from workers import VoiceWorker, TextWorker

logger = get_logger("MainWindow")

class MainWindow(QMainWindow):
    """Main Application Window for Cute JARVIS Desktop AI Assistant."""

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

        # Active worker references
        self.active_voice_worker: Optional[VoiceWorker] = None
        self.active_text_worker: Optional[TextWorker] = None

        self._setup_window_properties()
        self._setup_ui()
        self._connect_signals()
        self._setup_shortcuts()
        self._load_initial_data()
        self._check_initial_hardware()

    def _setup_window_properties(self):
        """Configure main window dimensions and metadata."""
        self.setWindowTitle("Cute JARVIS // AI Desktop Assistant")
        self.resize(1060, 720)
        self.setMinimumSize(880, 620)
        self.setStyleSheet(get_application_stylesheet())

    def _setup_ui(self):
        """Construct central widget and responsive layouts."""
        central_widget = QWidget()
        central_widget.setObjectName("root_container")
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Top Status & Title Bar
        self.status_bar = StatusBarWidget()
        root_layout.addWidget(self.status_bar)

        # Subtle divider
        top_divider = QFrame()
        top_divider.setFrameShape(QFrame.HLine)
        top_divider.setStyleSheet(f"background-color: {Palette.BORDER_DEFAULT}; max-height: 1px;")
        root_layout.addWidget(top_divider)

        # 2. Main Content Body (Splitter for Visualizer & Chat)
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(1)
        main_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {Palette.BORDER_DEFAULT};
            }}
        """)

        # Left Column: Avatar & Reactive Waveform Visualizer
        left_panel = QFrame()
        left_panel.setObjectName("avatar_panel")
        left_panel.setStyleSheet(f"""
            QFrame#avatar_panel {{
                background: qradialgradient(cx:0.5, cy:0.45, radius:0.8,
                    fx:0.5, fy:0.45, stop:0 #121730, stop:1 #0A0D18);
                border: none;
            }}
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)
        left_layout.setAlignment(Qt.AlignCenter)

        self.avatar_widget = AvatarWaveformWidget()
        left_layout.addWidget(self.avatar_widget, alignment=Qt.AlignCenter)

        main_splitter.addWidget(left_panel)

        # Right Column: Conversation History Feed
        right_panel = QFrame()
        right_panel.setObjectName("chat_panel")
        right_panel.setStyleSheet(f"""
            QFrame#chat_panel {{
                background-color: {Palette.BG_BASE};
                border: none;
            }}
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(0)

        self.conversation_panel = ConversationPanel()
        right_layout.addWidget(self.conversation_panel)

        main_splitter.addWidget(right_panel)

        # Responsive Splitter Ratio: 40% Visualizer, 60% Chat
        main_splitter.setSizes([420, 640])
        root_layout.addWidget(main_splitter, 1)

        # Subtle bottom divider
        bottom_divider = QFrame()
        bottom_divider.setFrameShape(QFrame.HLine)
        bottom_divider.setStyleSheet(f"background-color: {Palette.BORDER_DEFAULT}; max-height: 1px;")
        root_layout.addWidget(bottom_divider)

        # 3. Bottom Control Deck
        self.control_bar = ControlBarWidget(self.settings)
        root_layout.addWidget(self.control_bar)

    def _connect_signals(self):
        """Bind UI events, worker signals, and component actions."""
        # Top Bar
        self.status_bar.settings_clicked.connect(self._open_settings)

        # Visualizer Avatar
        self.avatar_widget.avatar_clicked.connect(self._on_avatar_clicked)

        # Bottom Controls
        self.control_bar.text_submitted.connect(self._handle_text_query)
        self.control_bar.mic_clicked.connect(self._toggle_voice_recognition)
        self.control_bar.mute_toggled.connect(self._on_mute_toggled)
        self.control_bar.language_switched.connect(self._on_language_switched)
        self.control_bar.voice_selected.connect(self._on_voice_selected)

        # Conversation Panel
        self.conversation_panel.sample_prompt_clicked.connect(self._handle_text_query)
        self.conversation_panel.clear_chat_clicked.connect(self._clear_conversation)

    def _setup_shortcuts(self):
        """Register productivity hotkeys."""
        # Ctrl + , -> Settings
        shortcut_settings = QShortcut(QKeySequence("Ctrl+,"), self)
        shortcut_settings.activated.connect(self._open_settings)

        # Ctrl + M -> Audio Mute
        shortcut_mute = QShortcut(QKeySequence("Ctrl+M"), self)
        shortcut_mute.activated.connect(self.control_bar._toggle_mute)

        # Ctrl + L -> Language Toggle
        shortcut_lang = QShortcut(QKeySequence("Ctrl+L"), self)
        shortcut_lang.activated.connect(self.control_bar._toggle_language)

    def _load_initial_data(self):
        """Load persistent conversation history from SQLite."""
        try:
            messages = self.repository.get_recent_messages(limit=30)
            self.conversation_panel.load_messages(messages)
            logger.info(f"Loaded {len(messages)} historical messages.")
        except Exception as e:
            logger.error(f"Error loading chat history: {e}")

    def _check_initial_hardware(self):
        """Diagnose microphone and OpenAI connectivity on startup."""
        # Check Microphone
        has_mic, mic_msg = self.stt_service.is_microphone_available()
        self.status_bar.set_mic_status(has_mic, "Ready" if has_mic else "No Device")
        if not has_mic:
            logger.warning(f"Microphone notice: {mic_msg}")

        # Check OpenAI
        is_configured = self.llm_service.is_configured()
        self.status_bar.set_openai_status(
            is_configured,
            "Connected" if is_configured else "Fallback"
        )

    def _on_avatar_clicked(self):
        """Clicking the avatar either starts listening or triggers a cute greeting."""
        if self.avatar_widget.state == AssistantState.IDLE:
            self._toggle_voice_recognition()
        elif self.avatar_widget.state == AssistantState.SPEAKING:
            self.audio_player.stop()

    def _on_mute_toggled(self, is_muted: bool):
        """Forward audio mute state to audio player."""
        self.audio_player.set_muted(is_muted)

    def _on_language_switched(self, new_lang: str):
        """Handle language switch event."""
        logger.info(f"Language changed to: {new_lang}")
        greeting = (
            "Ji Sir! Main ab Hindi mein baat karne ke liye taiyar hoon!"
            if new_lang.startswith("hi")
            else "Language switched to English, Sir!"
        )
        self.status_bar.set_state(AssistantState.IDLE, custom_text=f"● LANGUAGE: {new_lang}")

    def _on_voice_selected(self, voice_id: str):
        """Handle cute voice profile selection."""
        logger.info(f"Voice selected: {voice_id}")
        self.status_bar.set_state(AssistantState.IDLE, custom_text=f"● VOICE: {voice_id}")

    def _clear_conversation(self):
        """Confirm and clear conversation history."""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear your current conversation history?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.repository.clear_session()
            self.conversation_panel.clear_display()

    def _open_settings(self):
        """Display settings modal dialog."""
        dialog = SettingsDialog(self.settings, self)
        dialog.settings_applied.connect(self._on_settings_applied)
        dialog.exec()

    def _on_settings_applied(self):
        """Reconfigure services when user applies changes in Settings modal."""
        self.llm_service.refresh_client()
        self._check_initial_hardware()
        self.control_bar.populate_voices(self.settings.DEFAULT_LANGUAGE)
        logger.info("Settings successfully reloaded.")

    # -------------------------------------------------------------
    # Worker Thread Execution Pipelines
    # -------------------------------------------------------------
    def _toggle_voice_recognition(self):
        """Start or stop voice listening."""
        if self.active_voice_worker and self.active_voice_worker.isRunning():
            logger.info("Aborting current voice recognition loop.")
            self.active_voice_worker.abort()
            self.control_bar.set_mic_active(False)
            self._set_state(AssistantState.IDLE)
            return

        # Check if mic is available
        has_mic, _ = self.stt_service.is_microphone_available()
        if not has_mic:
            QMessageBox.information(
                self,
                "Microphone Required",
                "No active microphone was detected on this PC.\nPlease check your audio settings or type in the chat box!"
            )
            return

        self.control_bar.set_mic_active(True)
        self.control_bar.set_input_enabled(False)

        # Instantiate dedicated Voice Worker
        self.active_voice_worker = VoiceWorker(
            settings=self.settings,
            stt_service=self.stt_service,
            llm_service=self.llm_service,
            tts_service=self.tts_service,
            audio_player=self.audio_player,
            repository=self.repository,
            parent=self
        )

        self.active_voice_worker.state_changed.connect(self._on_worker_state_changed)
        self.active_voice_worker.status_text.connect(self._on_status_text_changed)
        self.active_voice_worker.audio_level.connect(self.avatar_widget.set_audio_amplitude)
        self.active_voice_worker.user_speech_ready.connect(self._on_user_message)
        self.active_voice_worker.assistant_reply_ready.connect(self._on_assistant_reply)
        self.active_voice_worker.error_occurred.connect(self._on_error)
        self.active_voice_worker.finished_cycle.connect(self._on_voice_finished)

        self.active_voice_worker.start()

    def _on_voice_finished(self):
        """Reset controls when voice cycle completes."""
        self.control_bar.set_mic_active(False)
        self.control_bar.set_input_enabled(True)
        self._set_state(AssistantState.IDLE)

    def _handle_text_query(self, query: str):
        """Process typed query from chat input or sample prompt chip."""
        if not query.strip():
            return

        # Disable input while processing
        self.control_bar.set_input_enabled(False)

        self.active_text_worker = TextWorker(
            query=query,
            settings=self.settings,
            llm_service=self.llm_service,
            tts_service=self.tts_service,
            audio_player=self.audio_player,
            repository=self.repository,
            parent=self
        )

        self.active_text_worker.state_changed.connect(self._on_worker_state_changed)
        self.active_text_worker.status_text.connect(self._on_status_text_changed)
        self.active_text_worker.audio_level.connect(self.avatar_widget.set_audio_amplitude)
        self.active_text_worker.user_message_ready.connect(self._on_user_message)
        self.active_text_worker.assistant_reply_ready.connect(self._on_assistant_reply)
        self.active_text_worker.error_occurred.connect(self._on_error)
        self.active_text_worker.finished_cycle.connect(self._on_text_finished)

        self.active_text_worker.start()

    def _on_text_finished(self):
        """Re-enable input when text query completes."""
        self.control_bar.set_input_enabled(True)
        self._set_state(AssistantState.IDLE)

    def _set_state(self, state: AssistantState, custom_text: str = ""):
        """Propagate state change to avatar and status bar."""
        self.avatar_widget.set_state(state)
        self.status_bar.set_state(state, custom_text)

    def _on_worker_state_changed(self, state_str: str):
        """Handle state notification from background worker."""
        try:
            state = AssistantState(state_str)
            self._set_state(state)
        except ValueError:
            pass

    def _on_status_text_changed(self, text: str):
        """Update top bar text description."""
        self.status_bar.state_pill.setText(f"● {text.upper()}")

    def _on_user_message(self, text: str, language: str):
        """Display incoming user message bubble."""
        self.conversation_panel.add_message(
            role="user",
            content=text,
            language=language
        )

    def _on_assistant_reply(self, text: str, language: str, audio_path: str):
        """Display incoming assistant reply bubble."""
        self.conversation_panel.add_message(
            role="assistant",
            content=text,
            language=language
        )

    def _on_error(self, title: str, message: str):
        """Display error alert in UI."""
        self._set_state(AssistantState.ERROR, custom_text=f"● {title.upper()}")
        logger.error(f"UI Alert: {title} - {message}")

    def closeEvent(self, event):
        """Clean up background workers and audio playback on exit."""
        logger.info("Shutting down Cute JARVIS...")
        if self.active_voice_worker and self.active_voice_worker.isRunning():
            self.active_voice_worker.abort()
            self.active_voice_worker.wait(1000)

        if self.active_text_worker and self.active_text_worker.isRunning():
            self.active_text_worker.abort()
            self.active_text_worker.wait(1000)

        self.audio_player.stop()
        super().closeEvent(event)
