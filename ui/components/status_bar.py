"""
Status Bar & Top Header Component.
Displays assistant branding, real-time operational status (Idle/Listening/Thinking/Speaking),
service health pills (OpenAI, Mic, Edge-TTS), and window management buttons.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame
)
from config.constants import AssistantState
from ui.styles.colors import Palette

class StatusBarWidget(QWidget):
    """Header bar with real-time state badge, service health indicators, and window controls."""

    minimize_clicked = Signal()
    maximize_clicked = Signal()
    close_clicked = Signal()
    settings_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # 1. Branding / Logo
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(8)

        logo_icon = QLabel("🌸")
        logo_icon.setStyleSheet("font-size: 18px;")
        brand_layout.addWidget(logo_icon)

        title_label = QLabel("CUTE JARVIS")
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 800;
            color: {Palette.TEXT_TITLE};
            letter-spacing: 1.5px;
        """)
        brand_layout.addWidget(title_label)

        sub_label = QLabel("// AI DESKTOP COMPANION")
        sub_label.setStyleSheet(f"""
            font-size: 10px;
            font-weight: 700;
            color: {Palette.CYAN};
            letter-spacing: 1px;
            margin-top: 2px;
        """)
        brand_layout.addWidget(sub_label)
        layout.addLayout(brand_layout)

        layout.addSpacing(16)

        # 2. Assistant State Pill
        self.state_pill = QLabel("● IDLE • READY")
        self.state_pill.setFixedHeight(26)
        self.state_pill.setAlignment(Qt.AlignCenter)
        self.set_state(AssistantState.IDLE)
        layout.addWidget(self.state_pill)

        layout.addStretch()

        # 3. Connection Status Indicators
        conn_layout = QHBoxLayout()
        conn_layout.setSpacing(10)

        # OpenAI Service Pill
        self.openai_indicator = QLabel("● AI: Active")
        self.set_openai_status(is_online=True, message="Active")
        conn_layout.addWidget(self.openai_indicator)

        # Mic Service Pill
        self.mic_indicator = QLabel("● MIC: Ready")
        self.set_mic_status(is_ready=True)
        conn_layout.addWidget(self.mic_indicator)

        # TTS Service Pill
        self.tts_indicator = QLabel("● TTS: Edge-Neural")
        self.tts_indicator.setStyleSheet(f"""
            background-color: {Palette.BG_SURFACE_LIGHT};
            color: {Palette.TEXT_SECONDARY};
            border: 1px solid {Palette.BORDER_DEFAULT};
            border-radius: 12px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 600;
        """)
        conn_layout.addWidget(self.tts_indicator)

        layout.addLayout(conn_layout)

        layout.addSpacing(12)

        # 4. Settings & Window Controls
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(6)

        # Settings Button
        settings_btn = QPushButton("⚙")
        settings_btn.setObjectName("settings_header_btn")
        settings_btn.setFixedSize(28, 28)
        settings_btn.setToolTip("Open Assistant Settings")
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.clicked.connect(self.settings_clicked.emit)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Palette.BG_SURFACE_LIGHT};
                color: {Palette.TEXT_SECONDARY};
                border: 1px solid {Palette.BORDER_DEFAULT};
                border-radius: 6px;
                font-size: 13px;
                padding: 0;
            }}
            QPushButton:hover {{
                background-color: {Palette.BG_HOVER};
                color: {Palette.CYAN};
                border: 1px solid {Palette.CYAN};
            }}
        """)
        ctrl_layout.addWidget(settings_btn)

        layout.addLayout(ctrl_layout)

    def set_state(self, state: AssistantState, custom_text: str = ""):
        """Update visual operational state badge."""
        if state == AssistantState.LISTENING:
            text = custom_text or "● LISTENING • SPEAK NOW"
            bg = "rgba(0, 240, 255, 0.15)"
            border = Palette.CYAN
            fg = Palette.CYAN
        elif state == AssistantState.THINKING:
            text = custom_text or "● THINKING • PROCESSING"
            bg = "rgba(138, 77, 255, 0.2)"
            border = Palette.PURPLE
            fg = Palette.PURPLE_LIGHT
        elif state == AssistantState.SPEAKING:
            text = custom_text or "● SPEAKING • VOICING"
            bg = "rgba(255, 92, 168, 0.2)"
            border = Palette.PINK
            fg = Palette.PINK
        elif state == AssistantState.ERROR:
            text = custom_text or "● ATTENTION • ERROR"
            bg = "rgba(255, 69, 101, 0.2)"
            border = Palette.STATE_ERROR
            fg = Palette.STATE_ERROR
        else:
            text = custom_text or "● IDLE • READY"
            bg = Palette.BG_SURFACE_LIGHT
            border = Palette.BORDER_DEFAULT
            fg = Palette.STATE_IDLE

        self.state_pill.setText(text)
        self.state_pill.setStyleSheet(f"""
            background-color: {bg};
            color: {fg};
            border: 1px solid {border};
            border-radius: 13px;
            padding: 3px 14px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
        """)

    def set_openai_status(self, is_online: bool, message: str = ""):
        """Update OpenAI status pill."""
        if is_online:
            fg = Palette.STATE_SUCCESS
            text = f"● AI: {message or 'Connected'}"
        else:
            fg = "#FFB300"
            text = f"● AI: {message or 'Fallback'}"

        self.openai_indicator.setText(text)
        self.openai_indicator.setStyleSheet(f"""
            background-color: {Palette.BG_SURFACE_LIGHT};
            color: {fg};
            border: 1px solid {Palette.BORDER_DEFAULT};
            border-radius: 12px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 600;
        """)

    def set_mic_status(self, is_ready: bool, message: str = ""):
        """Update microphone status pill."""
        if is_ready:
            fg = Palette.CYAN
            text = f"● MIC: {message or 'Ready'}"
        else:
            fg = Palette.STATE_ERROR
            text = f"● MIC: {message or 'Off'}"

        self.mic_indicator.setText(text)
        self.mic_indicator.setStyleSheet(f"""
            background-color: {Palette.BG_SURFACE_LIGHT};
            color: {fg};
            border: 1px solid {Palette.BORDER_DEFAULT};
            border-radius: 12px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 600;
        """)
