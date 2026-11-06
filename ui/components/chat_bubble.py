"""
Chat Message Bubble Component.
Renders stylish, rounded conversational bubbles with role badges,
timestamps, selectable text, and visual distinctions between User and Cute JARVIS.
"""

from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QTextEdit, QSizePolicy
)
from ui.styles.colors import Palette

class ChatBubble(QWidget):
    """Individual conversational chat bubble item."""

    def __init__(
        self,
        role: str,
        content: str,
        timestamp: str = "",
        language: str = "en-US",
        parent=None
    ):
        super().__init__(parent)
        self.role = role.lower()
        self.content = content.strip()
        self.language = language
        
        # Parse timestamp or default to now
        if not timestamp:
            self.time_str = datetime.now().strftime("%I:%M %p")
        else:
            try:
                dt = datetime.fromisoformat(timestamp)
                self.time_str = dt.strftime("%I:%M %p")
            except Exception:
                self.time_str = datetime.now().strftime("%I:%M %p")

        self._setup_ui()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(6, 4, 6, 4)
        root_layout.setSpacing(2)

        # Bubble Card Frame
        self.bubble_frame = QFrame()
        self.bubble_frame.setObjectName("chat_bubble_frame")
        
        bubble_layout = QVBoxLayout(self.bubble_frame)
        bubble_layout.setContentsMargins(14, 10, 14, 10)
        bubble_layout.setSpacing(6)

        # Header Row: Role Badge + Language Tag + Timestamp
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        is_assistant = (self.role == "assistant")

        # Role Badge
        role_label = QLabel()
        if is_assistant:
            role_label.setText("🌸 CUTE JARVIS")
            role_label.setStyleSheet(f"""
                color: {Palette.PINK};
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.5px;
            """)
        else:
            role_label.setText("👤 YOU")
            role_label.setStyleSheet(f"""
                color: {Palette.CYAN};
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.5px;
            """)
        header_layout.addWidget(role_label)

        # Language pill
        lang_label = QLabel("HI" if "hi" in self.language.lower() else "EN")
        lang_label.setStyleSheet(f"""
            background-color: {Palette.BG_BASE};
            color: {Palette.TEXT_MUTED};
            border: 1px solid {Palette.BORDER_DEFAULT};
            border-radius: 6px;
            padding: 1px 6px;
            font-size: 9px;
            font-weight: 600;
        """)
        header_layout.addWidget(lang_label)
        header_layout.addStretch()

        # Timestamp
        time_label = QLabel(self.time_str)
        time_label.setStyleSheet(f"""
            color: {Palette.TEXT_MUTED};
            font-size: 10px;
        """)
        header_layout.addWidget(time_label)

        bubble_layout.addLayout(header_layout)

        # Message Content Label
        message_label = QLabel(self.content)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        message_label.setStyleSheet(f"""
            color: {Palette.TEXT_PRIMARY};
            font-size: 13px;
            line-height: 1.45;
            background: transparent;
            border: none;
        """)
        bubble_layout.addWidget(message_label)

        # Frame Styling
        if is_assistant:
            self.bubble_frame.setStyleSheet(f"""
                QFrame#chat_bubble_frame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #151A33, stop:1 #1A1838);
                    border: 1px solid {Palette.BORDER_PURPLE};
                    border-left: 3px solid {Palette.PINK};
                    border-radius: 14px;
                }}
            """)
            root_layout.addWidget(self.bubble_frame, alignment=Qt.AlignLeft)
        else:
            self.bubble_frame.setStyleSheet(f"""
                QFrame#chat_bubble_frame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #111B34, stop:1 #0E253B);
                    border: 1px solid #1E3A5A;
                    border-right: 3px solid {Palette.CYAN};
                    border-radius: 14px;
                }}
            """)
            root_layout.addWidget(self.bubble_frame, alignment=Qt.AlignRight)
