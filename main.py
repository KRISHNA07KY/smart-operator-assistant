"""
Caterpillar (CAT) Smart Operator Assistant - In-Cab Intelligent Qt Dashboard
Main Application Entry Point.
"""

import sys
import os
import threading
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame, QButtonGroup, QStatusBar
)
from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QIcon, QFont, QKeySequence, QShortcut
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from PySide6.QtWebChannel import QWebChannel

from config import (
    GLOBAL_STYLESHEET, CAT_YELLOW, CAT_BLACK, CAT_DARK_BG,
    CAT_CARD_BG, CAT_BORDER, STATUS_DANGER, STATUS_SAFE, STATUS_WARNING
)
from utils.icon_manager import get_icon
from widgets.header_bar import HeaderBar
from widgets.tab_tasks import TasksTab
from widgets.tab_safety import SafetyTab
from widgets.tab_estimator import EstimatorTab
from widgets.tab_telemetry import TelemetryTab
from widgets.tab_training import TrainingTab

from backend.app import start_server
from backend.bridge import CatBridge


class MainWindow(QMainWindow):
    def __init__(self, server_url: str = "http://127.0.0.1:5173"):
        super().__init__()
        self.server_url = server_url
        self.setWindowTitle("CAT Smart Operator Assistant — In-Cab Intelligent Companion")
        self.resize(1440, 920)
        self.setMinimumSize(1100, 720)
        
        # Set dark industrial window styling
        self.setStyleSheet(GLOBAL_STYLESHEET + """
            QMainWindow {
                background-color: #0d1114;
            }
            QStatusBar {
                background-color: #12161a;
                color: #838e99;
                font-size: 11px;
                border-top: 1px solid #23282e;
            }
        """)

        self._init_bridge()
        self._init_ui()
        self._setup_shortcuts()

    def _init_bridge(self):
        self.channel = QWebChannel(self)
        self.bridge = CatBridge(self)
        self.channel.registerObject("catBridge", self.bridge)

    def _init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralContainer")
        self.setCentralWidget(central_widget)
        
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Top In-Cab Bar with Mode Switcher
        self.top_strip = self._create_top_strip()
        root_layout.addWidget(self.top_strip)

        # Central Stack containing:
        # Index 0: 3D Smart Operator Assistant (Replicated Repo UI with 3D & i18n)
        # Index 1: In-Cab Native Widgets View
        self.central_stack = QStackedWidget()

        # View 0: 3D WebEngine Assistant
        self.web_view = self._create_web_view()
        self.central_stack.addWidget(self.web_view)

        # View 1: Native In-Cab Widgets Cockpit
        self.native_view = self._create_native_cockpit()
        self.central_stack.addWidget(self.native_view)

        root_layout.addWidget(self.central_stack, stretch=1)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("🟢 CAT Assistant Engine Active • 3D Hardware Accelerated (60 FPS) • Multi-Lingual (EN/TA/HI/TE) Ready")

    def _create_top_strip(self) -> QFrame:
        strip = QFrame()
        strip.setFixedHeight(44)
        strip.setStyleSheet("""
            QFrame {
                background-color: #12161a;
                border-bottom: 1px solid #23282e;
                padding: 0 12px;
            }
        """)
        layout = QHBoxLayout(strip)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(10)

        # Brand Tag
        lbl_cat = QLabel("CAT")
        lbl_cat.setStyleSheet(f"background-color: {CAT_YELLOW}; color: #000; font-weight: 900; font-size: 13px; padding: 2px 8px; border-radius: 3px;")
        layout.addWidget(lbl_cat)

        lbl_title = QLabel("SMART OPERATOR ASSISTANT")
        lbl_title.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        layout.addWidget(lbl_title)

        lbl_badge = QLabel("• 3D DIGITAL TWIN & SIMULATOR")
        lbl_badge.setStyleSheet(f"color: {CAT_YELLOW}; font-size: 11px; font-weight: 600;")
        layout.addWidget(lbl_badge)

        layout.addStretch()

        # View Mode Toggle Buttons
        self.btn_mode_3d = QPushButton(" 3D Assistant (Full Experience)")
        self.btn_mode_3d.setIcon(get_icon("play", "#000000", 14))
        self.btn_mode_3d.setCheckable(True)
        self.btn_mode_3d.setChecked(True)
        self.btn_mode_3d.setCursor(Qt.PointingHandCursor)
        self.btn_mode_3d.setStyleSheet(f"""
            QPushButton {{
                background-color: #23282e;
                color: #C9D3DC;
                border: 1px solid #35404c;
                border-radius: 4px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:checked {{
                background-color: {CAT_YELLOW};
                color: #000000;
                border: 1px solid {CAT_YELLOW};
                font-weight: bold;
            }}
        """)
        self.btn_mode_3d.clicked.connect(self._switch_to_3d_mode)
        layout.addWidget(self.btn_mode_3d)

        self.btn_mode_widgets = QPushButton(" In-Cab Widgets (Classic)")
        self.btn_mode_widgets.setIcon(get_icon("sliders", "#C9D3DC", 14))
        self.btn_mode_widgets.setCheckable(True)
        self.btn_mode_widgets.setChecked(False)
        self.btn_mode_widgets.setCursor(Qt.PointingHandCursor)
        self.btn_mode_widgets.setStyleSheet(f"""
            QPushButton {{
                background-color: #23282e;
                color: #C9D3DC;
                border: 1px solid #35404c;
                border-radius: 4px;
                padding: 5px 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:checked {{
                background-color: {CAT_YELLOW};
                color: #000000;
                border: 1px solid {CAT_YELLOW};
                font-weight: bold;
            }}
        """)
        self.btn_mode_widgets.clicked.connect(self._switch_to_widgets_mode)
        layout.addWidget(self.btn_mode_widgets)

        # Fullscreen Button
        btn_fs = QPushButton(" ⛶ Fullscreen (F11)")
        btn_fs.setCursor(Qt.PointingHandCursor)
        btn_fs.setStyleSheet("""
            QPushButton {
                background-color: #1a1f26;
                color: #838e99;
                border: 1px solid #2d3640;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #242c36;
                color: #FFFFFF;
            }
        """)
        btn_fs.clicked.connect(self._toggle_fullscreen)
        layout.addWidget(btn_fs)

        return strip

    def _create_web_view(self) -> QWebEngineView:
        view = QWebEngineView()
        
        # Configure hardware acceleration & WebGL
        settings = view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        
        # Attach QtWebChannel to page
        view.page().setWebChannel(self.channel)
        
        # Load local server URL
        view.setUrl(QUrl(self.server_url))
        return view

    def _create_native_cockpit(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # In-Cab Header Bar
        self.header_bar = HeaderBar(self)
        layout.addWidget(self.header_bar)

        # Workspace with sidebar and stack
        workspace = QWidget()
        ws_layout = QHBoxLayout(workspace)
        ws_layout.setContentsMargins(0, 0, 0, 0)
        ws_layout.setSpacing(0)

        # Left Sidebar
        self.sidebar = self._create_native_sidebar()
        ws_layout.addWidget(self.sidebar)

        # Native Views Stack
        self.native_stack = QStackedWidget()
        self.tab_tasks = TasksTab(self)
        self.tab_safety = SafetyTab(self)
        self.tab_estimator = EstimatorTab(self)
        self.tab_telemetry = TelemetryTab(self)
        self.tab_training = TrainingTab(self)

        self.native_stack.addWidget(self.tab_tasks)
        self.native_stack.addWidget(self.tab_safety)
        self.native_stack.addWidget(self.tab_estimator)
        self.native_stack.addWidget(self.tab_telemetry)
        self.native_stack.addWidget(self.tab_training)
        self.stack = self.native_stack  # Backwards compatibility alias

        ws_layout.addWidget(self.native_stack, stretch=1)
        layout.addWidget(workspace)

        # Connect seatbelt signal
        self.tab_safety.seatbelt_changed.connect(self._on_seatbelt_status_changed)

        return container

    def _create_native_sidebar(self) -> QFrame:
        nav_frame = QFrame()
        nav_frame.setObjectName("sideNav")
        layout = QVBoxLayout(nav_frame)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(4)

        nav_label = QLabel("  CAB NAVIGATION")
        nav_label.setStyleSheet("color: #757575; font-size: 11px; font-weight: bold; letter-spacing: 1px; margin-bottom: 6px;")
        layout.addWidget(nav_label)

        self.native_nav_group = QButtonGroup(self)
        self.native_nav_group.setExclusive(True)

        nav_items = [
            ("tasks", "Daily Tasks", 0),
            ("safety", "Safety & Hazards", 1),
            ("estimator", "Time Estimator (AI)", 2),
            ("telemetry", "Telemetry & Idling", 3),
            ("training", "Training Hub", 4),
        ]

        for icon_key, text, index in nav_items:
            btn = QPushButton(f"  {text}")
            btn.setObjectName("navButton")
            btn.setIcon(get_icon(icon_key, CAT_YELLOW, 20))
            btn.setIconSize(QSize(20, 20))
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: #C0C0C0;
                    text-align: left;
                    padding: 13px 18px;
                    font-size: 13px;
                    font-weight: 600;
                    border: none;
                    border-left: 4px solid transparent;
                    border-radius: 0px;
                }}
                QPushButton:hover {{
                    background-color: #242424;
                    color: #FFFFFF;
                }}
                QPushButton:checked {{
                    background-color: #332A06;
                    color: {CAT_YELLOW};
                    border-left: 4px solid {CAT_YELLOW};
                    font-weight: bold;
                }}
            """)
            if index == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, idx=index: self.native_stack.setCurrentIndex(idx))
            self.native_nav_group.addButton(btn, index)
            layout.addWidget(btn)

        layout.addStretch()

        # Demo Controls
        demo_box = QFrame()
        demo_box.setStyleSheet("background-color: #1A1A1A; border: 1px solid #333333; border-radius: 6px; margin: 12px; padding: 10px;")
        demo_lay = QVBoxLayout(demo_box)
        demo_lay.setSpacing(6)

        lbl_demo = QLabel("CAB DEMO CONTROLS")
        lbl_demo.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {CAT_YELLOW}; letter-spacing: 0.5px;")
        demo_lay.addWidget(lbl_demo)

        btn_demo_sb = QPushButton(" Toggle Seatbelt")
        btn_demo_sb.setIcon(get_icon("refresh", "#FFFFFF", 14))
        btn_demo_sb.setStyleSheet("font-size: 11px; padding: 6px;")
        btn_demo_sb.clicked.connect(lambda: self.tab_safety._toggle_seatbelt())
        demo_lay.addWidget(btn_demo_sb)

        btn_demo_rad = QPushButton(" Toggle Radar Hazard")
        btn_demo_rad.setIcon(get_icon("alert-triangle", "#FFFFFF", 14))
        btn_demo_rad.setStyleSheet("font-size: 11px; padding: 6px;")
        btn_demo_rad.clicked.connect(lambda: self.tab_safety._toggle_radar_hazard())
        demo_lay.addWidget(btn_demo_rad)

        layout.addWidget(demo_box)
        return nav_frame

    def _switch_to_3d_mode(self):
        self.btn_mode_3d.setChecked(True)
        self.btn_mode_widgets.setChecked(False)
        self.central_stack.setCurrentIndex(0)
        self.status_bar.showMessage("🟢 CAT Assistant Active • Showing 3D Digital Twin, Multi-Lingual Assistant, and Simulator")

    def _switch_to_widgets_mode(self):
        self.btn_mode_3d.setChecked(False)
        self.btn_mode_widgets.setChecked(True)
        self.central_stack.setCurrentIndex(1)
        self.status_bar.showMessage("🟢 In-Cab Native Widgets Mode Active • Showing Classic QWidgets Cockpit")

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("F11"), self, self._toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+R"), self, lambda: self.web_view.reload())

    def _on_seatbelt_status_changed(self, is_fastened: bool):
        if not is_fastened:
            self.header_bar.set_alert_status("SEATBELT UNFASTENED — HAZARD", is_critical=True)
        else:
            self.header_bar.set_alert_status("2 ANOMALIES LOGGED (IDLE & LOGS)", is_normal=False)


def main():
    # Start local Python backend HTTP server
    srv, port = start_server(port=5173)
    server_thread = threading.Thread(target=srv.serve_forever, daemon=True)
    server_thread.start()
    server_url = f"http://127.0.0.1:{port}"
    print(f"[CAT-BACKEND] Local Assistant Server running at {server_url}")

    app = QApplication(sys.argv)
    window = MainWindow(server_url)
    window.show()
    
    exit_code = app.exec()
    srv.shutdown()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
