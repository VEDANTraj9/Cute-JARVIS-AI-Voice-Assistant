"""
Qt Style Sheets (QSS) for Cute JARVIS.
Applies futuristic navy, purple, cyan, and pink glow aesthetics across all components.
"""

from .colors import Palette

def get_application_stylesheet() -> str:
    """Return the master application QSS stylesheet."""
    return f"""
    /* Global Application Styles */
    QMainWindow, QWidget#root_container {{
        background-color: {Palette.BG_BASE};
        color: {Palette.TEXT_PRIMARY};
        font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
        font-size: 13px;
    }}

    /* Card Panels & Containers */
    QFrame.card_panel {{
        background-color: {Palette.BG_SURFACE};
        border: 1px solid {Palette.BORDER_DEFAULT};
        border-radius: 14px;
    }}

    QFrame.glass_panel {{
        background-color: rgba(16, 20, 38, 0.85);
        border: 1px solid {Palette.BORDER_PURPLE};
        border-radius: 16px;
    }}

    /* Scroll Areas */
    QScrollArea {{
        background: transparent;
        border: none;
    }}

    QScrollBar:vertical {{
        border: none;
        background: {Palette.BG_BASE};
        width: 6px;
        margin: 4px 0 4px 0;
        border-radius: 3px;
    }}

    QScrollBar::handle:vertical {{
        background: {Palette.BORDER_PURPLE};
        min-height: 25px;
        border-radius: 3px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {Palette.CYAN};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
        background: none;
    }}

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    /* Text Inputs */
    QLineEdit, QTextEdit {{
        background-color: {Palette.BG_INPUT};
        border: 1px solid {Palette.BORDER_DEFAULT};
        border-radius: 12px;
        color: {Palette.TEXT_PRIMARY};
        padding: 10px 14px;
        font-size: 13px;
        selection-background-color: {Palette.PURPLE};
    }}

    QLineEdit:focus, QTextEdit:focus {{
        border: 1px solid {Palette.CYAN};
        background-color: {Palette.BG_SURFACE_LIGHT};
    }}

    QLineEdit:disabled {{
        color: {Palette.TEXT_MUTED};
        background-color: {Palette.BG_BASE};
        border: 1px solid {Palette.BORDER_DEFAULT};
    }}

    /* Standard Interactive Buttons */
    QPushButton {{
        background-color: {Palette.BG_SURFACE_LIGHT};
        border: 1px solid {Palette.BORDER_DEFAULT};
        border-radius: 10px;
        color: {Palette.TEXT_PRIMARY};
        padding: 8px 16px;
        font-weight: 600;
        font-size: 13px;
    }}

    QPushButton:hover {{
        background-color: {Palette.BG_HOVER};
        border: 1px solid {Palette.PURPLE_LIGHT};
        color: {Palette.TEXT_TITLE};
    }}

    QPushButton:pressed {{
        background-color: {Palette.PURPLE_DIM};
    }}

    /* Glowing Primary Action Button */
    QPushButton#primary_button {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {Palette.PURPLE}, stop:1 #5B2CDE);
        border: 1px solid {Palette.PURPLE_LIGHT};
        border-radius: 12px;
        color: #FFFFFF;
        padding: 9px 20px;
        font-weight: 700;
        font-size: 13px;
    }}

    QPushButton#primary_button:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9D68FF, stop:1 #6B3CEE);
        border: 1px solid {Palette.CYAN};
    }}

    QPushButton#primary_button:pressed {{
        background: {Palette.PURPLE_DIM};
    }}

    /* Cyan Send Button */
    QPushButton#send_button {{
        background-color: {Palette.CYAN};
        border: none;
        border-radius: 12px;
        color: {Palette.BG_BASE};
        padding: 10px 20px;
        font-weight: 700;
        font-size: 13px;
    }}

    QPushButton#send_button:hover {{
        background-color: {Palette.CYAN_LIGHT};
    }}

    QPushButton#send_button:pressed {{
        background-color: {Palette.CYAN_DIM};
    }}

    QPushButton#send_button:disabled {{
        background-color: {Palette.BG_SURFACE_LIGHT};
        color: {Palette.TEXT_MUTED};
    }}

    /* Window Header Titlebar & Action Icons */
    QPushButton.icon_button {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        color: {Palette.TEXT_SECONDARY};
        padding: 6px;
    }}

    QPushButton.icon_button:hover {{
        background-color: {Palette.BG_SURFACE_LIGHT};
        border: 1px solid {Palette.BORDER_PURPLE};
        color: {Palette.CYAN};
    }}

    QPushButton#close_btn:hover {{
        background-color: #E81123;
        color: #FFFFFF;
        border: none;
    }}

    /* Dropdowns / ComboBoxes */
    QComboBox {{
        background-color: {Palette.BG_INPUT};
        border: 1px solid {Palette.BORDER_DEFAULT};
        border-radius: 10px;
        padding: 7px 12px;
        color: {Palette.TEXT_PRIMARY};
        font-size: 12px;
        min-width: 130px;
    }}

    QComboBox:hover {{
        border: 1px solid {Palette.PURPLE};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {Palette.BG_SURFACE};
        border: 1px solid {Palette.BORDER_PURPLE};
        border-radius: 8px;
        selection-background-color: {Palette.PURPLE};
        selection-color: #FFFFFF;
        color: {Palette.TEXT_PRIMARY};
        padding: 4px;
        outline: none;
    }}

    /* Sliders */
    QSlider::groove:horizontal {{
        height: 6px;
        background: {Palette.BG_INPUT};
        border-radius: 3px;
    }}

    QSlider::sub-page:horizontal {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {Palette.PURPLE}, stop:1 {Palette.CYAN});
        border-radius: 3px;
    }}

    QSlider::handle:horizontal {{
        background: {Palette.CYAN};
        border: 2px solid {Palette.BG_BASE};
        width: 16px;
        margin-top: -5px;
        margin-bottom: -5px;
        border-radius: 8px;
    }}

    QSlider::handle:horizontal:hover {{
        background: {Palette.CYAN_LIGHT};
        transform: scale(1.1);
    }}

    /* Tooltips */
    QToolTip {{
        background-color: {Palette.BG_SURFACE_LIGHT};
        color: {Palette.TEXT_PRIMARY};
        border: 1px solid {Palette.BORDER_PURPLE};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }}

    /* Status Pills / Badges */
    QLabel.badge {{
        background-color: {Palette.BG_SURFACE_LIGHT};
        border: 1px solid {Palette.BORDER_DEFAULT};
        border-radius: 12px;
        padding: 4px 12px;
        font-size: 11px;
        font-weight: 600;
    }}
    """
