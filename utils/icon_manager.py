"""
Icon Manager & Renderer
Loads web-scraped SVG vector icons from assets/icons, tints them with CAT brand colors,
and returns crisp QIcon or QPixmap objects for PySide6 widgets.
"""

import os
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QByteArray, QSize, Qt

import sys

if getattr(sys, 'frozen', False):
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    ICONS_DIR = os.path.abspath(os.path.join(base_dir, "assets", "icons"))
    if not os.path.exists(ICONS_DIR):
        ICONS_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.executable), "assets", "icons"))
else:
    ICONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "icons"))
_PIXMAP_CACHE = {}

def get_svg_content(name: str) -> str:
    path = os.path.join(ICONS_DIR, f"{name}.svg")
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def get_pixmap(name: str, color: str = "#FFFFFF", size: int = 20) -> QPixmap:
    """
    Renders an SVG icon into a high-DPI QPixmap with the requested color and size.
    """
    cache_key = (name, color, size)
    if cache_key in _PIXMAP_CACHE:
        return _PIXMAP_CACHE[cache_key]

    raw_svg = get_svg_content(name)
    if not raw_svg:
        # Fallback blank pixmap
        return QPixmap(size, size)

    # Tint SVG by replacing stroke attributes
    # Lucide icons use stroke="currentColor"
    tinted_svg = raw_svg.replace('stroke="currentColor"', f'stroke="{color}"')
    if 'stroke="' not in tinted_svg:
        tinted_svg = tinted_svg.replace('<svg ', f'<svg stroke="{color}" ')

    byte_array = QByteArray(tinted_svg.encode("utf-8"))
    renderer = QSvgRenderer(byte_array)

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    _PIXMAP_CACHE[cache_key] = pixmap
    return pixmap

def get_icon(name: str, color: str = "#FFFFFF", size: int = 20) -> QIcon:
    """
    Returns a QIcon for buttons, menus, and actions.
    """
    pixmap = get_pixmap(name, color, size)
    return QIcon(pixmap)

def create_icon_label(icon_name: str, color: str, text: str, size: int = 16, style_extra: str = ""):
    """
    Creates a QWidget containing an icon pixmap and text side-by-side.
    """
    from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(6)

    icon_lbl = QLabel()
    icon_lbl.setPixmap(get_pixmap(icon_name, color, size))
    lay.addWidget(icon_lbl)

    text_lbl = QLabel(text)
    if style_extra:
        text_lbl.setStyleSheet(style_extra)
    lay.addWidget(text_lbl)
    return w

