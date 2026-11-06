"""
Conversation History Panel Component.
Houses the scrolling conversational message list, empty state greeting card,
interactive sample prompt chips, and history clearance.
"""

from typing import List, Callable, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QPushButton, QFrame, QSizePolicy
)
from storage.models import ChatMessage
from ui.styles.colors import Palette
from .chat_bubble import ChatBubble

class ConversationPanel(QWidget):
    """Scrollable chat history with animated bubbles and quick prompt chips."""

    sample_prompt_clicked = Signal(str)
    clear_chat_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.message_count = 0
        self._setup_ui()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(6)

        # Header bar with message count & Clear button
        panel_header = QHBoxLayout()
        panel_header.setContentsMargins(8, 2, 8, 4)

        self.title_label = QLabel("💬 CONVERSATION FEED")
        self.title_label.setStyleSheet(f"""
            color: {Palette.TEXT_SECONDARY};
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
        """)
        panel_header.addWidget(self.title_label)

        panel_header.addStretch()

        clear_btn = QPushButton("🗑 Clear Feed")
        clear_btn.setFixedHeight(24)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setToolTip("Clear current conversation history")
        clear_btn.clicked.connect(self.clear_chat_clicked.emit)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {Palette.BORDER_DEFAULT};
                border-radius: 6px;
                color: {Palette.TEXT_MUTED};
                font-size: 10px;
                padding: 2px 8px;
            }}
            QPushButton:hover {{
                border-color: {Palette.STATE_ERROR};
                color: {Palette.STATE_ERROR};
                background: rgba(255, 69, 101, 0.1);
            }}
        """)
        panel_header.addWidget(clear_btn)
        root_layout.addLayout(panel_header)

        # Scroll Area for Messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Container widget inside scroll area
        self.container_widget = QWidget()
        self.container_widget.setObjectName("chat_container")
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setContentsMargins(8, 8, 8, 8)
        self.container_layout.setSpacing(8)
        self.container_layout.addStretch()

        self.scroll_area.setWidget(self.container_widget)
        root_layout.addWidget(self.scroll_area)

        # Show initial empty state
        self._show_empty_state()

    def _show_empty_state(self):
        """Display cute welcome card with interactive prompt chips."""
        self.empty_card = QFrame()
        self.empty_card.setObjectName("empty_state_card")
        self.empty_card.setStyleSheet(f"""
            QFrame#empty_state_card {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(22, 28, 54, 0.7), stop:1 rgba(16, 20, 38, 0.7));
                border: 1px dashed {Palette.BORDER_PURPLE};
                border-radius: 16px;
                padding: 16px;
            }}
        """)
        
        card_layout = QVBoxLayout(self.empty_card)
        card_layout.setSpacing(10)
        card_layout.setAlignment(Qt.AlignCenter)

        greet_icon = QLabel("🌸✨")
        greet_icon.setStyleSheet("font-size: 26px;")
        greet_icon.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(greet_icon)

        greet_title = QLabel("System Online & Awaiting Command, Sir!")
        greet_title.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 700;
            color: {Palette.TEXT_TITLE};
        """)
        greet_title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(greet_title)

        greet_desc = QLabel("Speak through your microphone or type your query below.\nClick any prompt chip to try:")
        greet_desc.setStyleSheet(f"""
            font-size: 12px;
            color: {Palette.TEXT_SECONDARY};
            line-height: 1.4;
        """)
        greet_desc.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(greet_desc)

        # Prompt chips row
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(8)
        chips_layout.setAlignment(Qt.AlignCenter)

        sample_prompts = [
            "What time is it?",
            "नमस्ते! आप कैसी हैं?",
            "Tell me something witty!",
            "Who created you?"
        ]

        for prompt in sample_prompts:
            chip = QPushButton(prompt)
            chip.setCursor(Qt.PointingHandCursor)
            chip.setStyleSheet(f"""
                QPushButton {{
                    background: {Palette.BG_SURFACE_LIGHT};
                    border: 1px solid {Palette.BORDER_PURPLE};
                    border-radius: 12px;
                    color: {Palette.CYAN};
                    padding: 6px 12px;
                    font-size: 11px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: {Palette.BG_HOVER};
                    border-color: {Palette.CYAN};
                    color: #FFFFFF;
                }}
            """)
            chip.clicked.connect(lambda _, p=prompt: self.sample_prompt_clicked.emit(p))
            chips_layout.addWidget(chip)

        card_layout.addLayout(chips_layout)

        # Insert at top of container layout
        self.container_layout.insertWidget(0, self.empty_card)

    def _remove_empty_state(self):
        """Remove empty greeting card when first message arrives."""
        if hasattr(self, "empty_card") and self.empty_card is not None:
            self.container_layout.removeWidget(self.empty_card)
            self.empty_card.deleteLater()
            self.empty_card = None

    def add_message(
        self,
        role: str,
        content: str,
        timestamp: str = "",
        language: str = "en-US"
    ):
        """Append a new message bubble to the chat feed."""
        self._remove_empty_state()
        self.message_count += 1

        bubble = ChatBubble(
            role=role,
            content=content,
            timestamp=timestamp,
            language=language
        )
        
        # Insert before bottom stretch
        idx = max(0, self.container_layout.count() - 1)
        self.container_layout.insertWidget(idx, bubble)

        # Scroll to bottom smoothly
        self.scroll_to_bottom()

    def load_messages(self, messages: List[ChatMessage]):
        """Load list of messages from persistent repository."""
        self.clear_display()
        if not messages:
            self._show_empty_state()
            return

        for msg in messages:
            self.add_message(
                role=msg.role,
                content=msg.content,
                timestamp=msg.created_at,
                language=msg.language
            )

    def clear_display(self):
        """Clear all messages in the view."""
        while self.container_layout.count() > 1:
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.message_count = 0
        self._show_empty_state()

    def scroll_to_bottom(self):
        """Scroll the feed to the latest message."""
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))
