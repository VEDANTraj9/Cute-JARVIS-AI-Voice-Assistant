"""
Settings Modal Dialog Component.
Provides user controls for OpenAI API key, model selection, voice modulation (pitch/rate),
microphone sensitivity, and ambient noise calibration.
"""

from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSlider, QCheckBox, QFrame,
    QTabWidget, QMessageBox, QGroupBox
)
from config.settings import AppSettings
from config.constants import BASE_DIR, VOICE_CATALOG
from ui.styles.colors import Palette

class SettingsDialog(QDialog):
    """Futuristic settings modal for full assistant customization."""

    settings_applied = Signal()

    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings // Cute JARVIS Configuration")
        self.setFixedSize(540, 560)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._setup_ui()
        self._load_current_values()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(16)

        # Header Title
        title_box = QHBoxLayout()
        icon_lbl = QLabel("⚙")
        icon_lbl.setStyleSheet(f"font-size: 20px; color: {Palette.CYAN};")
        title_box.addWidget(icon_lbl)

        title_text = QLabel("PREFERENCES & SYSTEM CONFIG")
        title_text.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 800;
            color: {Palette.TEXT_TITLE};
            letter-spacing: 1.5px;
        """)
        title_box.addWidget(title_text)
        title_box.addStretch()
        root_layout.addLayout(title_box)

        # Tabs Widget
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {Palette.BORDER_PURPLE};
                background: {Palette.BG_SURFACE};
                border-radius: 12px;
                padding: 12px;
            }}
            QTabBar::tab {{
                background: {Palette.BG_BASE};
                color: {Palette.TEXT_SECONDARY};
                padding: 8px 18px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background: {Palette.BG_SURFACE};
                color: {Palette.CYAN};
                border: 1px solid {Palette.BORDER_PURPLE};
                border-bottom: none;
            }}
        """)

        # Tab 1: AI Brain
        brain_tab = self._create_brain_tab()
        tabs.addTab(brain_tab, "🤖 AI Intelligence")

        # Tab 2: Voice & Audio
        voice_tab = self._create_voice_tab()
        tabs.addTab(voice_tab, "🎙 Speech & Audio")

        root_layout.addWidget(tabs)

        # Bottom Actions: Save, Cancel
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        action_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(90, 36)
        cancel_btn.clicked.connect(self.reject)
        action_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save & Apply")
        save_btn.setObjectName("primary_button")
        save_btn.setFixedSize(130, 36)
        save_btn.clicked.connect(self._save_settings)
        action_layout.addWidget(save_btn)

        root_layout.addLayout(action_layout)

    def _create_brain_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        # API Key
        key_lbl = QLabel("OpenAI API Secret Key:")
        key_lbl.setStyleSheet(f"color: {Palette.TEXT_PRIMARY}; font-weight: 600;")
        layout.addWidget(key_lbl)

        key_box = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("sk-proj-...")
        key_box.addWidget(self.api_key_input)

        self.show_key_btn = QPushButton("👁")
        self.show_key_btn.setFixedSize(36, 36)
        self.show_key_btn.setToolTip("Show / Hide Key")
        self.show_key_btn.clicked.connect(self._toggle_key_visibility)
        key_box.addWidget(self.show_key_btn)
        layout.addLayout(key_box)

        # Model Selector
        model_lbl = QLabel("OpenAI Chat Model:")
        model_lbl.setStyleSheet(f"color: {Palette.TEXT_PRIMARY}; font-weight: 600;")
        layout.addWidget(model_lbl)

        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
        layout.addWidget(self.model_combo)

        # User Preferred Title
        title_lbl = QLabel("Preferred Title (How JARVIS addresses you):")
        title_lbl.setStyleSheet(f"color: {Palette.TEXT_PRIMARY}; font-weight: 600;")
        layout.addWidget(title_lbl)

        self.user_title_input = QLineEdit()
        self.user_title_input.setPlaceholderText("e.g., Sir, Boss, Master")
        layout.addWidget(self.user_title_input)

        layout.addStretch()
        return widget

    def _create_voice_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        # Voice Pitch
        pitch_box = QHBoxLayout()
        pitch_lbl = QLabel("Cute Voice Pitch:")
        pitch_lbl.setStyleSheet(f"color: {Palette.TEXT_PRIMARY}; font-weight: 600;")
        pitch_box.addWidget(pitch_lbl)

        self.pitch_val_lbl = QLabel("+5Hz")
        self.pitch_val_lbl.setStyleSheet(f"color: {Palette.CYAN}; font-weight: 700;")
        pitch_box.addWidget(self.pitch_val_lbl)
        layout.addLayout(pitch_box)

        self.pitch_slider = QSlider(Qt.Horizontal)
        self.pitch_slider.setRange(-15, 20)
        self.pitch_slider.setValue(5)
        self.pitch_slider.valueChanged.connect(
            lambda v: self.pitch_val_lbl.setText(f"{'+' if v>=0 else ''}{v}Hz")
        )
        layout.addWidget(self.pitch_slider)

        # Voice Rate
        rate_box = QHBoxLayout()
        rate_lbl = QLabel("Speech Speed Rate:")
        rate_lbl.setStyleSheet(f"color: {Palette.TEXT_PRIMARY}; font-weight: 600;")
        rate_box.addWidget(rate_lbl)

        self.rate_val_lbl = QLabel("+0%")
        self.rate_val_lbl.setStyleSheet(f"color: {Palette.CYAN}; font-weight: 700;")
        rate_box.addWidget(self.rate_val_lbl)
        layout.addLayout(rate_box)

        self.rate_slider = QSlider(Qt.Horizontal)
        self.rate_slider.setRange(-20, 30)
        self.rate_slider.setValue(0)
        self.rate_slider.valueChanged.connect(
            lambda v: self.rate_val_lbl.setText(f"{'+' if v>=0 else ''}{v}%")
        )
        layout.addWidget(self.rate_slider)

        # Mic Energy Threshold
        mic_box = QHBoxLayout()
        mic_lbl = QLabel("Mic Energy Threshold (Silence Gate):")
        mic_lbl.setStyleSheet(f"color: {Palette.TEXT_PRIMARY}; font-weight: 600;")
        mic_box.addWidget(mic_lbl)

        self.mic_val_lbl = QLabel("300")
        self.mic_val_lbl.setStyleSheet(f"color: {Palette.CYAN}; font-weight: 700;")
        mic_box.addWidget(self.mic_val_lbl)
        layout.addLayout(mic_box)

        self.mic_slider = QSlider(Qt.Horizontal)
        self.mic_slider.setRange(100, 1000)
        self.mic_slider.setValue(300)
        self.mic_slider.valueChanged.connect(lambda v: self.mic_val_lbl.setText(str(v)))
        layout.addWidget(self.mic_slider)

        # Dynamic Energy Threshold Checkbox
        self.dyn_check = QCheckBox("Enable dynamic ambient noise adjustment")
        self.dyn_check.setStyleSheet(f"color: {Palette.TEXT_SECONDARY};")
        layout.addWidget(self.dyn_check)

        layout.addStretch()
        return widget

    def _toggle_key_visibility(self):
        if self.api_key_input.echoMode() == QLineEdit.Password:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.show_key_btn.setText("🔒")
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.show_key_btn.setText("👁")

    def _load_current_values(self):
        """Populate controls with active settings."""
        self.api_key_input.setText(self.settings.OPENAI_API_KEY)
        idx = self.model_combo.findText(self.settings.OPENAI_MODEL)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)

        self.user_title_input.setText(self.settings.USER_NAME)

        # Pitch
        try:
            val_pitch = int(self.settings.VOICE_PITCH.replace("Hz", "").replace("+", ""))
            self.pitch_slider.setValue(val_pitch)
        except Exception:
            self.pitch_slider.setValue(5)

        # Rate
        try:
            val_rate = int(self.settings.VOICE_RATE.replace("%", "").replace("+", ""))
            self.rate_slider.setValue(val_rate)
        except Exception:
            self.rate_slider.setValue(0)

        # Mic
        self.mic_slider.setValue(int(self.settings.MIC_ENERGY_THRESHOLD))
        self.dyn_check.setChecked(bool(self.settings.DYNAMIC_ENERGY_THRESHOLD))

    def _save_settings(self):
        """Persist settings to in-memory AppSettings and .env file."""
        self.settings.OPENAI_API_KEY = self.api_key_input.text().strip()
        self.settings.OPENAI_MODEL = self.model_combo.currentText()
        self.settings.USER_NAME = self.user_title_input.text().strip() or "Sir"

        pitch_val = self.pitch_slider.value()
        self.settings.VOICE_PITCH = f"{'+' if pitch_val >= 0 else ''}{pitch_val}Hz"

        rate_val = self.rate_slider.value()
        self.settings.VOICE_RATE = f"{'+' if rate_val >= 0 else ''}{rate_val}%"

        self.settings.MIC_ENERGY_THRESHOLD = self.mic_slider.value()
        self.settings.DYNAMIC_ENERGY_THRESHOLD = self.dyn_check.isChecked()

        # Update .env file safely
        env_file = BASE_DIR / ".env"
        try:
            env_content = f"""OPENAI_API_KEY={self.settings.OPENAI_API_KEY}
OPENAI_MODEL={self.settings.OPENAI_MODEL}
USER_NAME={self.settings.USER_NAME}
DEFAULT_LANGUAGE={self.settings.DEFAULT_LANGUAGE}
ENGLISH_VOICE={self.settings.ENGLISH_VOICE}
HINDI_VOICE={self.settings.HINDI_VOICE}
VOICE_RATE={self.settings.VOICE_RATE}
VOICE_PITCH={self.settings.VOICE_PITCH}
MIC_ENERGY_THRESHOLD={self.settings.MIC_ENERGY_THRESHOLD}
DYNAMIC_ENERGY_THRESHOLD={self.settings.DYNAMIC_ENERGY_THRESHOLD}
"""
            env_file.write_text(env_content, encoding="utf-8")
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not write to .env file: {e}")

        self.settings_applied.emit()
        self.accept()
