"""
Control Bar Component.
Features the glowing circular microphone trigger button, text query input,
send button, audio mute toggle, language selector, and voice selector.
"""

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QComboBox, QLabel, QFrame
)
from config.constants import VOICE_CATALOG
from config.settings import AppSettings
from ui.styles.colors import Palette

class ControlBarWidget(QWidget):
    """Bottom control deck with mic button, text chat input, and speech options."""

    text_submitted = Signal(str)           # When user presses Send or Enter
    mic_clicked = Signal()                 # Mic button pressed
    mute_toggled = Signal(bool)            # Audio mute toggled (True = muted)
    language_switched = Signal(str)        # "en-US" or "hi-IN"
    voice_selected = Signal(str)           # Voice ID

    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.is_mic_active = False
        self.is_muted = False
        self._setup_ui()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 8, 16, 12)
        root_layout.setSpacing(8)

        # 1. Top Control Strip: Audio Mute, Language Pill, Voice Picker
        meta_strip = QHBoxLayout()
        meta_strip.setContentsMargins(4, 0, 4, 0)
        meta_strip.setSpacing(10)

        # Audio Mute Toggle Button
        self.mute_btn = QPushButton("🔊")
        self.mute_btn.setFixedSize(32, 30)
        self.mute_btn.setToolTip("Mute/Unmute Assistant Voice Output")
        self.mute_btn.setCursor(Qt.PointingHandCursor)
        self.mute_btn.clicked.connect(self._toggle_mute)
        meta_strip.addWidget(self.mute_btn)

        # Language Selector Button (EN / HI toggle)
        self.lang_btn = QPushButton("🌐 English (US)")
        self.lang_btn.setFixedHeight(30)
        self.lang_btn.setToolTip("Switch language between English and Hindi")
        self.lang_btn.setCursor(Qt.PointingHandCursor)
        self.lang_btn.clicked.connect(self._toggle_language)
        self._update_lang_btn_style()
        meta_strip.addWidget(self.lang_btn)

        # Voice Selector Dropdown
        voice_label = QLabel("Voice:")
        voice_label.setStyleSheet(f"color: {Palette.TEXT_SECONDARY}; font-size: 11px; font-weight: 600;")
        meta_strip.addWidget(voice_label)

        self.voice_combo = QComboBox()
        self.voice_combo.setFixedHeight(30)
        self.voice_combo.currentIndexChanged.connect(self._on_voice_changed)
        meta_strip.addWidget(self.voice_combo)

        meta_strip.addStretch()

        # Voice Mode Hint
        self.hint_label = QLabel("Press Space or click Mic to speak")
        self.hint_label.setStyleSheet(f"color: {Palette.TEXT_MUTED}; font-size: 11px;")
        meta_strip.addWidget(self.hint_label)

        root_layout.addLayout(meta_strip)

        # 2. Main Input & Mic Action Row
        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 0, 0, 0)
        input_row.setSpacing(10)

        # Glowing Circular Microphone Button
        self.mic_btn = QPushButton("🎙")
        self.mic_btn.setObjectName("mic_button")
        self.mic_btn.setFixedSize(46, 46)
        self.mic_btn.setToolTip("Click to Start Listening")
        self.mic_btn.setCursor(Qt.PointingHandCursor)
        self.mic_btn.clicked.connect(self.mic_clicked.emit)
        self.set_mic_active(False)
        input_row.addWidget(self.mic_btn)

        # Text Query Line Edit
        self.text_input = QLineEdit()
        self.text_input.setObjectName("chat_input")
        self.text_input.setPlaceholderText("Type your message or ask JARVIS anything... (Press Enter to send)")
        self.text_input.setFixedHeight(46)
        self.text_input.returnPressed.connect(self._submit_text)
        input_row.addWidget(self.text_input)

        # Send Button
        self.send_btn = QPushButton("Send ➤")
        self.send_btn.setObjectName("send_button")
        self.send_btn.setFixedHeight(46)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.clicked.connect(self._submit_text)
        input_row.addWidget(self.send_btn)

        root_layout.addLayout(input_row)

        # Populate voices based on initial language
        self.populate_voices(self.settings.DEFAULT_LANGUAGE)

    def _toggle_mute(self):
        self.is_muted = not self.is_muted
        self.mute_btn.setText("🔇" if self.is_muted else "🔊")
        self.mute_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {"#3A1A22" if self.is_muted else Palette.BG_SURFACE_LIGHT};
                color: {Palette.STATE_ERROR if self.is_muted else Palette.TEXT_PRIMARY};
                border: 1px solid {Palette.STATE_ERROR if self.is_muted else Palette.BORDER_DEFAULT};
                border-radius: 6px;
                font-size: 13px;
            }}
        """)
        self.mute_toggled.emit(self.is_muted)

    def _toggle_language(self):
        """Toggle between English and Hindi."""
        current_lang = self.settings.DEFAULT_LANGUAGE
        new_lang = "hi-IN" if current_lang.startswith("en") else "en-US"
        self.settings.DEFAULT_LANGUAGE = new_lang
        self._update_lang_btn_style()
        self.populate_voices(new_lang)
        self.language_switched.emit(new_lang)

    def _update_lang_btn_style(self):
        is_hindi = self.settings.DEFAULT_LANGUAGE.startswith("hi")
        label = "🇮🇳 हिन्दी (Hindi)" if is_hindi else "🇺🇸 English (US)"
        border_col = Palette.PINK if is_hindi else Palette.CYAN
        self.lang_btn.setText(label)
        self.lang_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Palette.BG_INPUT};
                color: {Palette.TEXT_PRIMARY};
                border: 1px solid {border_col};
                border-radius: 8px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {Palette.BG_HOVER};
            }}
        """)

    def populate_voices(self, language: str):
        """Populate the voice selector according to active language catalog."""
        self.voice_combo.blockSignals(True)
        self.voice_combo.clear()

        catalog_key = "hi-IN" if language.startswith("hi") else "en-US"
        voices = VOICE_CATALOG.get(catalog_key, [])
        active_id = self.settings.get_active_voice()

        selected_idx = 0
        for i, voice in enumerate(voices):
            self.voice_combo.addItem(voice["name"], userData=voice["id"])
            if voice["id"] == active_id:
                selected_idx = i

        self.voice_combo.setCurrentIndex(selected_idx)
        self.voice_combo.blockSignals(False)

    def _on_voice_changed(self, index: int):
        if index >= 0:
            voice_id = self.voice_combo.itemData(index)
            if voice_id:
                if self.settings.DEFAULT_LANGUAGE.startswith("hi"):
                    self.settings.HINDI_VOICE = voice_id
                else:
                    self.settings.ENGLISH_VOICE = voice_id
                self.voice_selected.emit(voice_id)

    def set_mic_active(self, active: bool):
        """Update microphone button glow state."""
        self.is_mic_active = active
        if active:
            self.mic_btn.setStyleSheet(f"""
                QPushButton#mic_button {{
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.7,
                        fx:0.5, fy:0.5, stop:0 {Palette.CYAN}, stop:1 #008899);
                    border: 2px solid #FFFFFF;
                    border-radius: 23px;
                    color: {Palette.BG_BASE};
                    font-size: 20px;
                }}
            """)
            self.hint_label.setText("● Listening to your voice... Speak now!")
            self.hint_label.setStyleSheet(f"color: {Palette.CYAN}; font-size: 11px; font-weight: 600;")
        else:
            self.mic_btn.setStyleSheet(f"""
                QPushButton#mic_button {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #1A1F3C, stop:1 #11152B);
                    border: 2px solid {Palette.BORDER_PURPLE};
                    border-radius: 23px;
                    color: {Palette.CYAN};
                    font-size: 19px;
                }}
                QPushButton#mic_button:hover {{
                    border: 2px solid {Palette.CYAN};
                    background-color: {Palette.BG_HOVER};
                }}
            """)
            self.hint_label.setText("Press Space or click Mic to speak")
            self.hint_label.setStyleSheet(f"color: {Palette.TEXT_MUTED}; font-size: 11px;")

    def _submit_text(self):
        """Handle submit action."""
        text = self.text_input.text().strip()
        if text:
            self.text_input.clear()
            self.text_submitted.emit(text)

    def set_input_enabled(self, enabled: bool):
        """Enable or disable input fields during processing."""
        self.text_input.setEnabled(enabled)
        self.send_btn.setEnabled(enabled)
        if enabled:
            self.text_input.setFocus()
