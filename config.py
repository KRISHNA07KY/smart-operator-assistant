"""
Caterpillar (CAT) Dashboard Configuration & Theme
Authentic industrial black and yellow styling for in-cab touch displays.
"""

CAT_YELLOW = "#FFCD11"
CAT_YELLOW_HOVER = "#E5B80E"
CAT_YELLOW_DARK = "#CCA000"
CAT_BLACK = "#121212"
CAT_DARK_BG = "#181818"
CAT_CARD_BG = "#222222"
CAT_CARD_HOVER = "#2A2A2A"
CAT_BORDER = "#383838"
CAT_BORDER_LIGHT = "#4A4A4A"

TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#C0C0C0"
TEXT_MUTED = "#888888"

STATUS_SAFE = "#10B981"       # Green
STATUS_WARNING = "#F59E0B"    # Amber
STATUS_DANGER = "#EF4444"     # Red
STATUS_INFO = "#3B82F6"       # Blue

GLOBAL_STYLESHEET = f"""
QMainWindow {{
    background-color: {CAT_DARK_BG};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', Arial, sans-serif;
}}

QWidget {{
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}}

QLabel {{
    border: none;
    background: transparent;
}}

/* Top Header */
#headerBar {{
    background-color: {CAT_BLACK};
    border-bottom: 2px solid {CAT_YELLOW};
    padding: 8px 16px;
}}

/* Sidebar */
#sideNav {{
    background-color: {CAT_BLACK};
    border-right: 1px solid {CAT_BORDER};
    min-width: 220px;
    max-width: 240px;
}}

QPushButton#navButton {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    text-align: left;
    padding: 14px 18px;
    font-size: 14px;
    font-weight: 600;
    border: none;
    border-left: 4px solid transparent;
    border-radius: 0px;
}}

QPushButton#navButton:hover {{
    background-color: {CAT_CARD_BG};
    color: {TEXT_PRIMARY};
}}

QPushButton#navButton:checked {{
    background-color: #2D2506;
    color: {CAT_YELLOW};
    border-left: 4px solid {CAT_YELLOW};
    font-weight: bold;
}}

/* Cards and Containers */
QFrame.cat-card {{
    background-color: {CAT_CARD_BG};
    border: 1px solid {CAT_BORDER};
    border-radius: 8px;
    padding: 14px;
}}

QFrame.cat-card QLabel {{
    border: none;
    background: transparent;
}}

/* Buttons */
QPushButton.btn-primary {{
    background-color: {CAT_YELLOW};
    color: #000000;
    font-weight: bold;
    font-size: 13px;
    border-radius: 6px;
    padding: 10px 18px;
    border: none;
}}

QPushButton.btn-primary:hover {{
    background-color: {CAT_YELLOW_HOVER};
}}

QPushButton.btn-primary:pressed {{
    background-color: {CAT_YELLOW_DARK};
}}

QPushButton.btn-secondary {{
    background-color: #2E2E2E;
    color: {TEXT_PRIMARY};
    font-weight: 600;
    font-size: 12px;
    border-radius: 6px;
    padding: 8px 14px;
    border: 1px solid {CAT_BORDER};
}}

QPushButton.btn-secondary:hover {{
    background-color: #3D3D3D;
    border-color: {CAT_YELLOW};
}}

QPushButton.btn-danger {{
    background-color: {STATUS_DANGER};
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    border-radius: 6px;
    padding: 8px 16px;
    border: none;
}}

/* Form Controls */
QLineEdit, QComboBox, QSpinBox, QTextEdit {{
    background-color: #1A1A1A;
    border: 1px solid {CAT_BORDER};
    border-radius: 6px;
    color: {TEXT_PRIMARY};
    padding: 7px 10px;
    font-size: 13px;
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {{
    border: 1px solid {CAT_YELLOW};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: #1F1F1F;
    border: 1px solid {CAT_BORDER};
    selection-background-color: {CAT_YELLOW};
    selection-color: #000000;
    color: {TEXT_PRIMARY};
}}

/* Checkboxes & Radio buttons */
QCheckBox, QRadioButton {{
    color: {TEXT_PRIMARY};
    spacing: 8px;
    font-size: 12px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    background-color: #1E1E1E;
    border: 1px solid {CAT_BORDER};
    border-radius: 3px;
}}

QRadioButton::indicator {{
    border-radius: 8px;
}}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {CAT_YELLOW};
    border-color: {CAT_YELLOW};
}}

/* Sliders */
QSlider::groove:horizontal {{
    height: 6px;
    background: #333333;
    border-radius: 3px;
}}

QSlider::sub-page:horizontal {{
    background: {CAT_YELLOW};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {CAT_YELLOW};
    border: 2px solid #FFFFFF;
    width: 18px;
    margin-top: -6px;
    margin-bottom: -6px;
    border-radius: 9px;
}}

/* Tables */
QTableWidget {{
    background-color: {CAT_CARD_BG};
    border: 1px solid {CAT_BORDER};
    border-radius: 8px;
    gridline-color: #282828;
    color: {TEXT_PRIMARY};
    selection-background-color: #383319;
    selection-color: {CAT_YELLOW};
}}

QTableWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid #282828;
}}

QHeaderView::section {{
    background-color: #151515;
    color: {TEXT_SECONDARY};
    font-weight: bold;
    font-size: 12px;
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid {CAT_YELLOW};
    text-transform: uppercase;
}}

/* Progress Bars */
QProgressBar {{
    background-color: #1A1A1A;
    border: 1px solid {CAT_BORDER};
    border-radius: 6px;
    text-align: center;
    color: #FFFFFF;
    font-weight: bold;
    height: 18px;
}}

QProgressBar::chunk {{
    background-color: {CAT_YELLOW};
    border-radius: 5px;
}}
"""
