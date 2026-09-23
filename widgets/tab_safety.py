"""
Safety & Hazard Management Center Widget (Outcome 2)
Includes:
1. Real-time Seatbelt Compliance Monitor
2. 360° Proximity Hazard Radar (with animated sweep & hazard blips)
3. Incident & Working Conditions Logging System
"""

import math
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QProgressBar, QComboBox, QTextEdit, QLineEdit, QRadioButton,
    QButtonGroup, QCheckBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QTimer, QPointF, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient
from config import (
    CAT_YELLOW, CAT_BLACK, CAT_CARD_BG, CAT_BORDER, STATUS_SAFE,
    STATUS_WARNING, STATUS_DANGER, STATUS_INFO, TEXT_MUTED, TEXT_SECONDARY
)
from utils.icon_manager import get_pixmap, get_icon
from models.dummy_incident import get_initial_incidents, IncidentReport


class ProximityRadarWidget(QWidget):
    """
    Custom 360-degree In-Cab Radar visualizer showing machinery in center
    and detected obstacles / personnel with safety zones.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(280, 280)
        self.sweep_angle = 0
        self.hazard_active = True
        self.hazard_distance = 3.8  # meters
        self.hazard_azimuth = 210   # degrees (rear-left blind spot)

        # Radar sweep animation timer
        self.sweep_timer = QTimer(self)
        self.sweep_timer.timeout.connect(self._rotate_sweep)
        self.sweep_timer.start(40)

    def _rotate_sweep(self):
        self.sweep_angle = (self.sweep_angle + 3) % 360
        self.update()

    def set_hazard(self, active: bool, dist: float = 3.8, azimuth: float = 210):
        self.hazard_active = active
        self.hazard_distance = dist
        self.hazard_azimuth = azimuth
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 20

        # 1. Dark radar background
        painter.setBrush(QBrush(QColor(15, 23, 18)))
        painter.setPen(QPen(QColor(40, 60, 45), 2))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)

        # 2. Concentric Zone Rings
        # Green Zone (>10m outer)
        painter.setPen(QPen(QColor(16, 185, 129, 60), 1, Qt.DashLine))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)

        # Amber Warning Zone (5m - 10m)
        r_amber = radius * 0.65
        painter.setPen(QPen(QColor(245, 158, 11, 100), 1, Qt.DashLine))
        painter.drawEllipse(QPointF(center_x, center_y), r_amber, r_amber)

        # Red Critical Danger Zone (< 5m)
        r_danger = radius * 0.35
        painter.setPen(QPen(QColor(239, 68, 68, 150), 2, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(239, 68, 68, 25)))
        painter.drawEllipse(QPointF(center_x, center_y), r_danger, r_danger)
        painter.setBrush(Qt.NoBrush)

        # 3. Crosshairs
        painter.setPen(QPen(QColor(45, 75, 55), 1))
        painter.drawLine(center_x - radius, center_y, center_x + radius, center_y)
        painter.drawLine(center_x, center_y - radius, center_x, center_y + radius)

        # 4. Sweep Line & Faint Glow
        rad_sweep = math.radians(self.sweep_angle)
        sweep_x = center_x + radius * math.cos(rad_sweep)
        sweep_y = center_y + radius * math.sin(rad_sweep)

        sweep_pen = QPen(QColor(255, 205, 17, 180), 2)
        painter.setPen(sweep_pen)
        painter.drawLine(center_x, center_y, sweep_x, sweep_y)

        # 5. Center Machine Marker (Excavator Icon representation)
        painter.setBrush(QBrush(QColor(255, 205, 17)))
        painter.setPen(QPen(Qt.black, 1.5))
        painter.drawRoundedRect(center_x - 12, center_y - 16, 24, 32, 4, 4)
        
        # Excavator Boom Indicator pointing forward (up)
        painter.setBrush(QBrush(Qt.black))
        painter.drawRect(center_x - 3, center_y - 26, 6, 12)

        # 6. Render Detected Hazard Blip (Ground worker in rear blind spot)
        if self.hazard_active:
            rad_haz = math.radians(self.hazard_azimuth)
            # map distance: 0m -> center, 15m -> radius
            haz_r = (self.hazard_distance / 15.0) * radius
            haz_x = center_x + haz_r * math.cos(rad_haz)
            haz_y = center_y + haz_r * math.sin(rad_haz)

            # Pulsing hazard halo
            painter.setBrush(QBrush(QColor(239, 68, 68, 120)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(haz_x, haz_y), 14, 14)

            # Hazard center dot
            painter.setBrush(QBrush(QColor(255, 50, 50)))
            painter.setPen(QPen(Qt.white, 2))
            painter.drawEllipse(QPointF(haz_x, haz_y), 6, 6)

            # Hazard label
            painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
            painter.setPen(QPen(QColor(255, 200, 200)))
            painter.drawText(haz_x + 10, haz_y - 5, f"WORKER ({self.hazard_distance}m)")

        # Distance rings text
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QPen(QColor(160, 160, 160)))
        painter.drawText(center_x + 4, center_y - r_danger + 12, "5m")
        painter.drawText(center_x + 4, center_y - r_amber + 12, "10m")
        painter.drawText(center_x + 4, center_y - radius + 14, "15m")


class SafetyTab(QWidget):
    seatbelt_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.incidents = get_initial_incidents()
        self.seatbelt_fastened = True
        self.flash_state = False
        self._init_ui()

        # Seatbelt alert flash timer
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self._flash_seatbelt)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Page Title
        title = QLabel("OPERATOR SAFETY & REAL-TIME HAZARD CENTER")
        title.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {CAT_YELLOW}; letter-spacing: 0.5px;")
        main_layout.addWidget(title)

        # Top Section: Two Columns (Left: Seatbelt Monitor, Right: Proximity Hazard Radar)
        top_row = QHBoxLayout()
        top_row.setSpacing(18)

        # -----------------------------
        # 1. SEATBELT COMPLIANCE PANEL
        # -----------------------------
        self.seatbelt_card = QFrame()
        self.seatbelt_card.setProperty("class", "cat-card")
        self.seatbelt_card.setMinimumWidth(360)
        sb_layout = QVBoxLayout(self.seatbelt_card)
        sb_layout.setSpacing(12)

        sb_header = QLabel("1. SEATBELT COMPLIANCE MONITOR")
        sb_header.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {CAT_YELLOW};")
        sb_layout.addWidget(sb_header)

        # Big Visual Status Indicator
        self.sb_indicator_frame = QFrame()
        self.sb_indicator_frame.setObjectName("sbIndicatorFrame")
        self.sb_indicator_frame.setStyleSheet(f"""
            QFrame#sbIndicatorFrame {{
                background-color: #152E1D;
                border: 2px solid {STATUS_SAFE};
                border-radius: 8px;
                padding: 12px;
            }}
            QFrame#sbIndicatorFrame QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        sb_ind_layout = QVBoxLayout(self.sb_indicator_frame)
        sb_ind_layout.setAlignment(Qt.AlignCenter)

        self.sb_icon = QLabel()
        self.sb_icon.setPixmap(get_pixmap("shield-check", STATUS_SAFE, 44))
        self.sb_icon.setAlignment(Qt.AlignCenter)
        sb_ind_layout.addWidget(self.sb_icon)

        self.sb_status_text = QLabel("SEATBELT FASTENED")
        self.sb_status_text.setStyleSheet(f"font-size: 18px; font-weight: 900; color: {STATUS_SAFE}; letter-spacing: 1px;")
        self.sb_status_text.setAlignment(Qt.AlignCenter)
        sb_ind_layout.addWidget(self.sb_status_text)

        self.sb_subtext = QLabel("Cab latch sensor: SECURE  |  Interlock: CLEAR")
        self.sb_subtext.setStyleSheet("font-size: 11px; color: #B0B0B0;")
        self.sb_subtext.setAlignment(Qt.AlignCenter)
        sb_ind_layout.addWidget(self.sb_subtext)
        sb_layout.addWidget(self.sb_indicator_frame)

        # Shift Compliance Stats
        sb_stats_layout = QHBoxLayout()
        stat1 = QLabel("Shift Compliance:\n<b>75.0%</b> (2 Unfastened Events)")
        stat1.setStyleSheet("color: #FFFFFF; font-size: 12px;")
        stat2 = QLabel("Interlock Policy:\n<b>Warning & Fleet Log</b>")
        stat2.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        sb_stats_layout.addWidget(stat1)
        sb_stats_layout.addWidget(stat2)
        sb_layout.addLayout(sb_stats_layout)

        # Seatbelt Compliance Gauge
        self.sb_compliance_bar = QProgressBar()
        self.sb_compliance_bar.setRange(0, 100)
        self.sb_compliance_bar.setValue(75)
        self.sb_compliance_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #1A1A1A;
                border: 1px solid {CAT_BORDER};
                border-radius: 4px;
                text-align: center;
                color: white;
                font-weight: bold;
                height: 16px;
            }}
            QProgressBar::chunk {{
                background-color: {STATUS_WARNING};
                border-radius: 3px;
            }}
        """)
        sb_layout.addWidget(self.sb_compliance_bar)

        # Interactive Simulation Toggle
        self.btn_toggle_sb = QPushButton(" Toggle Seatbelt (Simulate Unfasten)")
        self.btn_toggle_sb.setIcon(get_icon("refresh", "#FFFFFF", 14))
        self.btn_toggle_sb.setProperty("class", "btn-secondary")
        self.btn_toggle_sb.clicked.connect(self._toggle_seatbelt)
        sb_layout.addWidget(self.btn_toggle_sb)
        top_row.addWidget(self.seatbelt_card)

        # -----------------------------
        # 2. PROXIMITY HAZARD RADAR
        # -----------------------------
        self.radar_card = QFrame()
        self.radar_card.setProperty("class", "cat-card")
        radar_layout = QVBoxLayout(self.radar_card)
        radar_layout.setSpacing(10)

        radar_top = QHBoxLayout()
        radar_header = QLabel("2. 360° PROXIMITY HAZARD RADAR & BLIND SPOTS")
        radar_header.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {CAT_YELLOW};")
        radar_top.addWidget(radar_header)
        radar_top.addStretch()

        self.btn_toggle_hazard = QPushButton(" Simulate Hazard Approach")
        self.btn_toggle_hazard.setIcon(get_icon("alert-triangle", "#FFFFFF", 14))
        self.btn_toggle_hazard.setProperty("class", "btn-secondary")
        self.btn_toggle_hazard.clicked.connect(self._toggle_radar_hazard)
        radar_top.addWidget(self.btn_toggle_hazard)
        radar_layout.addLayout(radar_top)

        radar_content = QHBoxLayout()
        # Radar Canvas
        self.radar_widget = ProximityRadarWidget()
        radar_content.addWidget(self.radar_widget)

        # Radar Legend and Alert Readouts
        radar_info = QVBoxLayout()
        radar_info.setSpacing(8)

        legend_title = QLabel("RADAR DETECTION ZONES")
        legend_title.setStyleSheet("font-weight: bold; font-size: 11px; color: #CCCCCC;")
        radar_info.addWidget(legend_title)

        zone_red = QLabel("🔴 Danger Zone (< 5m): Immediate Stop")
        zone_red.setStyleSheet(f"color: {STATUS_DANGER}; font-size: 12px; font-weight: bold;")
        zone_amber = QLabel("🟠 Warning Zone (5-10m): Caution / Horn")
        zone_amber.setStyleSheet(f"color: {STATUS_WARNING}; font-size: 12px; font-weight: bold;")
        zone_green = QLabel("🟢 Safe Zone (> 10m): Clear Swing")
        zone_green.setStyleSheet(f"color: {STATUS_SAFE}; font-size: 12px; font-weight: bold;")

        radar_info.addWidget(zone_red)
        radar_info.addWidget(zone_amber)
        radar_info.addWidget(zone_green)
        radar_info.addSpacing(10)

        # Real-time Proximity Alert Box
        self.proximity_banner = QFrame()
        self.proximity_banner.setObjectName("proxBanner")
        self.proximity_banner.setStyleSheet(f"""
            QFrame#proxBanner {{
                background-color: #381515;
                border: 2px solid {STATUS_DANGER};
                border-radius: 6px;
                padding: 10px;
            }}
            QFrame#proxBanner QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        prox_layout = QVBoxLayout(self.proximity_banner)
        self.prox_title = QLabel("⚠️ CRITICAL PROXIMITY ALERT")
        self.prox_title.setStyleSheet(f"color: {STATUS_DANGER}; font-weight: 900; font-size: 12px;")
        self.prox_desc = QLabel("Ground Personnel in REAR BLIND SPOT\nDistance: 3.8 meters | Azimuth: 210°")
        self.prox_desc.setStyleSheet("color: #FFFFFF; font-size: 11px;")
        prox_layout.addWidget(self.prox_title)
        prox_layout.addWidget(self.prox_desc)
        radar_info.addWidget(self.proximity_banner)

        radar_info.addStretch()
        radar_content.addLayout(radar_info)
        radar_layout.addLayout(radar_content)

        top_row.addWidget(self.radar_card)
        main_layout.addLayout(top_row)

        # ---------------------------------------------
        # 3. INCIDENT & WORKING CONDITIONS LOGGING
        # ---------------------------------------------
        incident_card = QFrame()
        incident_card.setProperty("class", "cat-card")
        inc_layout = QVBoxLayout(incident_card)
        inc_layout.setSpacing(12)

        inc_top = QHBoxLayout()
        inc_title = QLabel("3. INCIDENT & WORKING CONDITIONS LOGGING")
        inc_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {CAT_YELLOW};")
        inc_top.addWidget(inc_title)
        inc_top.addStretch()

        btn_export = QPushButton(" Export Log (JSON)")
        btn_export.setIcon(get_icon("save", "#FFFFFF", 14))
        btn_export.setProperty("class", "btn-secondary")
        btn_export.clicked.connect(self._export_log)
        inc_top.addWidget(btn_export)
        inc_layout.addLayout(inc_top)

        # Form + Table Split
        split_layout = QHBoxLayout()
        split_layout.setSpacing(16)

        # Log Form (Left)
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_frame.setStyleSheet("""
            QFrame#formFrame {
                background-color: #1E1E1E;
                border: 1px solid #383838;
                border-radius: 6px;
                padding: 12px;
            }
            QFrame#formFrame QLabel {
                border: none;
                background: transparent;
                color: #FFFFFF;
                font-weight: 600;
                font-size: 12px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(8)

        form_title = QLabel("Log Real-Time Safety Event / Condition")
        form_title.setStyleSheet("font-weight: bold; color: #FFFFFF;")
        form_layout.addWidget(form_title)

        form_layout.addWidget(QLabel("Incident Category:"))
        self.cb_category = QComboBox()
        self.cb_category.addItems([
            "Near Miss Incident",
            "Pedestrian in Swing Radius",
            "Seatbelt Non-Compliance",
            "Trench Wall Slump / Cave-in",
            "Machine Tilt / Rollover Hazard",
            "Severe Weather Hazard"
        ])
        form_layout.addWidget(self.cb_category)

        form_layout.addWidget(QLabel("Working Conditions / Weather Factors:"))
        self.chk_rain = QCheckBox("Heavy Rain / Muddy Soil")
        self.chk_rain.setChecked(True)
        self.chk_night = QCheckBox("Low Ambient Visibility / Dust")
        self.chk_slope = QCheckBox("Steep Incline / Unstable Slope")
        form_layout.addWidget(self.chk_rain)
        form_layout.addWidget(self.chk_night)
        form_layout.addWidget(self.chk_slope)

        form_layout.addWidget(QLabel("Severity:"))
        sev_layout = QHBoxLayout()
        self.rb_low = QRadioButton("Low")
        self.rb_med = QRadioButton("Medium")
        self.rb_high = QRadioButton("High")
        self.rb_high.setChecked(True)
        self.rb_crit = QRadioButton("Critical")
        sev_layout.addWidget(self.rb_low)
        sev_layout.addWidget(self.rb_med)
        sev_layout.addWidget(self.rb_high)
        sev_layout.addWidget(self.rb_crit)
        form_layout.addLayout(sev_layout)

        form_layout.addWidget(QLabel("Operator Observations / Location Notes:"))
        self.txt_notes = QTextEdit()
        self.txt_notes.setPlaceholderText("Enter details e.g. Worker walked into rear blind spot during trench excavation...")
        self.txt_notes.setMaximumHeight(42)
        form_layout.addWidget(self.txt_notes)

        btn_submit_incident = QPushButton(" Submit Official Safety Log")
        btn_submit_incident.setIcon(get_icon("zap", "#000000", 14))
        btn_submit_incident.setProperty("class", "btn-primary")
        btn_submit_incident.clicked.connect(self._submit_incident)
        form_layout.addWidget(btn_submit_incident)

        split_layout.addWidget(form_frame, stretch=4)

        # Incident History Table (Right)
        self.table_incidents = QTableWidget()
        self.table_incidents.setColumnCount(6)
        self.table_incidents.setHorizontalHeaderLabels([
            "ID", "Timestamp", "Category", "Severity", "Working Conditions", "Status"
        ])
        self.table_incidents.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_incidents.verticalHeader().setVisible(False)
        self.table_incidents.setSelectionBehavior(QTableWidget.SelectRows)
        split_layout.addWidget(self.table_incidents, stretch=6)

        inc_layout.addLayout(split_layout)
        main_layout.addWidget(incident_card, stretch=1)

        self._populate_incident_table()

    def _toggle_seatbelt(self):
        self.seatbelt_fastened = not self.seatbelt_fastened
        self.seatbelt_changed.emit(self.seatbelt_fastened)

        if not self.seatbelt_fastened:
            self.sb_icon.setPixmap(get_pixmap("alert-octagon", STATUS_DANGER, 44))
            self.sb_status_text.setText("UNFASTENED — CRITICAL HAZARD")
            self.sb_status_text.setStyleSheet(f"font-size: 18px; font-weight: 900; color: {STATUS_DANGER}; letter-spacing: 1px;")
            self.sb_subtext.setText("ALARM ACTIVE: Operator must fasten belt prior to machine motion!")
            self.btn_toggle_sb.setIcon(get_icon("check-circle", "#FFFFFF", 14))
            self.btn_toggle_sb.setText(" Fasten Seatbelt")
            self.flash_timer.start(500)
        else:
            self.flash_timer.stop()
            self.sb_icon.setPixmap(get_pixmap("shield-check", STATUS_SAFE, 44))
            self.sb_status_text.setText("SEATBELT FASTENED")
            self.sb_status_text.setStyleSheet(f"font-size: 18px; font-weight: 900; color: {STATUS_SAFE}; letter-spacing: 1px;")
            self.sb_subtext.setText("Cab latch sensor: SECURE  |  Interlock: CLEAR")
            self.sb_indicator_frame.setStyleSheet(f"""
                QFrame#sbIndicatorFrame {{
                    background-color: #152E1D;
                    border: 2px solid {STATUS_SAFE};
                    border-radius: 8px;
                    padding: 12px;
                }}
                QFrame#sbIndicatorFrame QLabel {{
                    border: none;
                    background: transparent;
                }}
            """)
            self.btn_toggle_sb.setIcon(get_icon("refresh", "#FFFFFF", 14))
            self.btn_toggle_sb.setText(" Toggle Seatbelt (Simulate Unfasten)")

    def _flash_seatbelt(self):
        self.flash_state = not self.flash_state
        bg = "#451515" if self.flash_state else "#250A0A"
        self.sb_indicator_frame.setStyleSheet(f"""
            QFrame#sbIndicatorFrame {{
                background-color: {bg};
                border: 2px solid {STATUS_DANGER};
                border-radius: 8px;
                padding: 12px;
            }}
            QFrame#sbIndicatorFrame QLabel {{
                border: none;
                background: transparent;
            }}
        """)

    def _toggle_radar_hazard(self):
        cur = self.radar_widget.hazard_active
        self.radar_widget.set_hazard(not cur)
        if not cur:
            self.btn_toggle_hazard.setText("Clear Hazard")
            self.proximity_banner.setVisible(True)
        else:
            self.btn_toggle_hazard.setText("Simulate Hazard Approach")
            self.proximity_banner.setVisible(False)

    def _populate_incident_table(self):
        self.table_incidents.setRowCount(len(self.incidents))
        for row, inc in enumerate(self.incidents):
            # ID
            id_item = QTableWidgetItem(inc.incident_id)
            id_item.setFont(self._bold_font())
            self.table_incidents.setItem(row, 0, id_item)

            # Timestamp
            self.table_incidents.setItem(row, 1, QTableWidgetItem(inc.timestamp))

            # Category
            self.table_incidents.setItem(row, 2, QTableWidgetItem(inc.category))

            # Severity
            sev_item = QTableWidgetItem(inc.severity)
            sev_item.setTextAlignment(Qt.AlignCenter)
            if inc.severity in ["High", "Critical"]:
                sev_item.setForeground(Qt.GlobalColor.red)
            elif inc.severity == "Medium":
                sev_item.setForeground(Qt.GlobalColor.yellow)
            else:
                sev_item.setForeground(Qt.GlobalColor.green)
            self.table_incidents.setItem(row, 3, sev_item)

            # Conditions
            self.table_incidents.setItem(row, 4, QTableWidgetItem(inc.working_conditions))

            # Status
            stat_item = QTableWidgetItem(inc.status)
            stat_item.setTextAlignment(Qt.AlignCenter)
            self.table_incidents.setItem(row, 5, stat_item)

    def _bold_font(self):
        f = self.font()
        f.setBold(True)
        return f

    def _submit_incident(self):
        # Determine severity
        sev = "Medium"
        if self.rb_crit.isChecked():
            sev = "Critical"
        elif self.rb_high.isChecked():
            sev = "High"
        elif self.rb_low.isChecked():
            sev = "Low"

        # Determine conditions
        conds = []
        if self.chk_rain.isChecked():
            conds.append("Heavy Rain / Mud")
        if self.chk_night.isChecked():
            conds.append("Low Visibility / Dust")
        if self.chk_slope.isChecked():
            conds.append("Steep Slope")
        cond_str = ", ".join(conds) if conds else "Normal Conditions"

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_inc = IncidentReport(
            incident_id=f"INC-2025-{len(self.incidents)+1:03d}",
            timestamp=now_str,
            category=self.cb_category.currentText(),
            severity=sev,
            working_conditions=cond_str,
            location="Zone B - Excavator EXC001",
            description=self.txt_notes.toPlainText() or "Operator logged hazardous condition.",
            reported_by="OP1001",
            status="Logged"
        )
        self.incidents.insert(0, new_inc)
        self._populate_incident_table()
        self.txt_notes.clear()
        QMessageBox.information(self, "Safety Event Logged", f"Safety event {new_inc.incident_id} successfully recorded and transmitted to fleet telemetry.")

    def _export_log(self):
        QMessageBox.information(self, "Export Log", f"Exported {len(self.incidents)} safety incident logs to JSON format.")
