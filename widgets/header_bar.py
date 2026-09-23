"""
Top In-Cab Header Bar Widget
Displays machinery identity, operator badge, live digital clock, alert banner, and SOS button.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QTime, QDate, Signal
from PySide6.QtGui import QFont
from config import CAT_YELLOW, CAT_BLACK, STATUS_DANGER, STATUS_SAFE, STATUS_WARNING, TEXT_MUTED
from utils.icon_manager import get_pixmap, get_icon

class HeaderBar(QFrame):
    sos_triggered = Signal()
    toggle_seatbelt_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("headerBar")
        self.setFixedHeight(75)
        self._init_ui()
        
        # Start digital clock timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        self._update_clock()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(16)

        # 1. CAT Machinery Branding Block
        cat_badge_layout = QHBoxLayout()
        cat_badge_layout.setSpacing(10)
        
        # Yellow CAT Icon Box
        cat_box = QLabel("CAT")
        cat_box.setStyleSheet(f"""
            background-color: {CAT_YELLOW};
            color: #000000;
            font-size: 20px;
            font-weight: 900;
            padding: 4px 10px;
            border-radius: 4px;
            letter-spacing: 1px;
        """)
        cat_badge_layout.addWidget(cat_box)

        # Model & Machine ID Info
        machine_info_layout = QVBoxLayout()
        machine_info_layout.setSpacing(1)
        machine_title = QLabel("320 GC EXCAVATOR")
        machine_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF;")
        
        machine_meta = QLabel("ID: EXC001  |  1,530.2 Engine Hrs")
        machine_meta.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED};")
        machine_info_layout.addWidget(machine_title)
        machine_info_layout.addWidget(machine_meta)
        cat_badge_layout.addLayout(machine_info_layout)
        layout.addLayout(cat_badge_layout)

        # Vertical Divider
        layout.addWidget(self._create_divider())

        # 2. Operator Profile Block
        operator_layout = QVBoxLayout()
        operator_layout.setSpacing(1)
        op_name = QLabel("OP1001 - John Doe")
        op_name.setStyleSheet("font-size: 13px; font-weight: bold; color: #FFFFFF;")
        
        op_skill_badge = QLabel("SKILL: INTERMEDIATE  •  SHIFT: 07:00 - 15:30")
        op_skill_badge.setStyleSheet(f"font-size: 11px; color: {CAT_YELLOW}; font-weight: 600;")
        operator_layout.addWidget(op_name)
        operator_layout.addWidget(op_skill_badge)
        layout.addLayout(operator_layout)

        layout.addStretch()

        # 3. Dynamic Global Alert Status Pill
        self.alert_pill = QFrame()
        self.alert_pill.setObjectName("alertPill")
        pill_layout = QHBoxLayout(self.alert_pill)
        pill_layout.setContentsMargins(10, 4, 10, 4)
        pill_layout.setSpacing(6)
        
        self.alert_icon_lbl = QLabel()
        self.alert_icon_lbl.setPixmap(get_pixmap("alert-triangle", STATUS_WARNING, 14))
        self.alert_text_lbl = QLabel("2 ANOMALIES DETECTED")
        self.alert_text_lbl.setStyleSheet(f"color: {STATUS_WARNING}; font-size: 12px; font-weight: bold;")
        pill_layout.addWidget(self.alert_icon_lbl)
        pill_layout.addWidget(self.alert_text_lbl)

        self.alert_pill.setStyleSheet(f"""
            QFrame#alertPill {{
                background-color: #382405;
                border: 1px solid {STATUS_WARNING};
                border-radius: 14px;
            }}
            QFrame#alertPill QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        layout.addWidget(self.alert_pill)

        # 4. Connectivity & Diagnostics Pill
        telemetry_status = QFrame()
        telemetry_status.setObjectName("telemetryStatus")
        tel_layout = QHBoxLayout(telemetry_status)
        tel_layout.setContentsMargins(10, 4, 10, 4)
        tel_layout.setSpacing(6)

        tel_icon = QLabel()
        tel_icon.setPixmap(get_pixmap("radio", STATUS_SAFE, 14))
        tel_text = QLabel("GPS 3D FIX  |  4G LTE")
        tel_text.setStyleSheet(f"color: {STATUS_SAFE}; font-size: 11px; font-weight: 600;")
        tel_layout.addWidget(tel_icon)
        tel_layout.addWidget(tel_text)

        telemetry_status.setStyleSheet(f"""
            QFrame#telemetryStatus {{
                background-color: #162418;
                border: 1px solid {STATUS_SAFE};
                border-radius: 14px;
            }}
            QFrame#telemetryStatus QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        layout.addWidget(telemetry_status)

        # Vertical Divider
        layout.addWidget(self._create_divider())

        # 5. Live Digital Clock
        clock_layout = QVBoxLayout()
        clock_layout.setSpacing(1)
        self.clock_label = QLabel("00:00:00")
        self.clock_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF; font-family: 'Consolas', monospace;")
        self.clock_label.setAlignment(Qt.AlignRight)
        
        self.date_label = QLabel("2025-05-02")
        self.date_label.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED};")
        self.date_label.setAlignment(Qt.AlignRight)
        
        clock_layout.addWidget(self.clock_label)
        clock_layout.addWidget(self.date_label)
        layout.addLayout(clock_layout)

        # 6. Emergency SOS Button
        self.sos_button = QPushButton(" EMERGENCY SOS")
        self.sos_button.setIcon(get_icon("alert-octagon", "#FFFFFF", 16))
        self.sos_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {STATUS_DANGER};
                color: #FFFFFF;
                font-weight: 800;
                font-size: 12px;
                border-radius: 6px;
                padding: 10px 16px;
                border: 2px solid #FF7777;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
        """)
        self.sos_button.clicked.connect(self._on_sos_clicked)
        layout.addWidget(self.sos_button)

    def _create_divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #383838;")
        return line

    def _update_clock(self):
        now = QTime.currentTime()
        today = QDate.currentDate()
        self.clock_label.setText(now.toString("HH:mm:ss"))
        self.date_label.setText(today.toString("ddd, MMM dd yyyy"))

    def set_alert_status(self, text: str, is_critical: bool = False, is_normal: bool = False):
        if is_critical:
            self.alert_icon_lbl.setPixmap(get_pixmap("alert-octagon", STATUS_DANGER, 14))
            self.alert_text_lbl.setText(text)
            self.alert_text_lbl.setStyleSheet(f"color: {STATUS_DANGER}; font-size: 12px; font-weight: bold;")
            self.alert_pill.setStyleSheet(f"""
                QFrame#alertPill {{
                    background-color: #381515;
                    border: 1px solid {STATUS_DANGER};
                    border-radius: 14px;
                }}
                QFrame#alertPill QLabel {{
                    border: none;
                    background: transparent;
                }}
            """)
        elif is_normal:
            self.alert_icon_lbl.setPixmap(get_pixmap("check-circle", STATUS_SAFE, 14))
            self.alert_text_lbl.setText(text)
            self.alert_text_lbl.setStyleSheet(f"color: {STATUS_SAFE}; font-size: 12px; font-weight: bold;")
            self.alert_pill.setStyleSheet(f"""
                QFrame#alertPill {{
                    background-color: #122818;
                    border: 1px solid {STATUS_SAFE};
                    border-radius: 14px;
                }}
                QFrame#alertPill QLabel {{
                    border: none;
                    background: transparent;
                }}
            """)
        else:
            self.alert_icon_lbl.setPixmap(get_pixmap("alert-triangle", STATUS_WARNING, 14))
            self.alert_text_lbl.setText(text)
            self.alert_text_lbl.setStyleSheet(f"color: {STATUS_WARNING}; font-size: 12px; font-weight: bold;")
            self.alert_pill.setStyleSheet(f"""
                QFrame#alertPill {{
                    background-color: #382405;
                    border: 1px solid {STATUS_WARNING};
                    border-radius: 14px;
                }}
                QFrame#alertPill QLabel {{
                    border: none;
                    background: transparent;
                }}
            """)

    def _on_sos_clicked(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("EMERGENCY OPERATOR ASSIST")
        msg.setIcon(QMessageBox.Critical)
        msg.setText("EMERGENCY BEACON TRIGGERED!\n\nFleet Operations Dispatcher & Site Medic have been alerted with machine GPS coordinates (Zone B - Excavator EXC001).")
        msg.setInformativeText("Press OK to maintain active broadcast or Cancel to silence.")
        msg.setStyleSheet("QMessageBox { background-color: #242424; color: white; } QPushButton { background-color: #EF4444; color: white; font-weight: bold; padding: 6px 14px; }")
        msg.exec()
        self.sos_triggered.emit()
