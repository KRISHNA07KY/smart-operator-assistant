"""
Telemetry & Anomaly Detection Widget (Outcome 4)
Identifies unusual machine behavior (excessive idling, unsafe operation, low duty cycles).
Renders the Image 2 historical dataset and provides visual trend charts.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QGridLayout, QMessageBox
)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from config import (
    CAT_YELLOW, CAT_BLACK, CAT_CARD_BG, CAT_BORDER, STATUS_SAFE,
    STATUS_WARNING, STATUS_DANGER, STATUS_INFO, TEXT_MUTED, TEXT_SECONDARY
)
from utils.icon_manager import get_icon, get_pixmap
from models.dummy_telemetry import get_initial_telemetry, evaluate_anomalies, TelemetryRecord


class TelemetryBarChart(QWidget):
    """
    Custom QPainter bar chart for Idling Time vs Load Cycles
    """
    def __init__(self, records, parent=None):
        super().__init__(parent)
        self.records = records
        self.setMinimumHeight(180)

    def set_records(self, records):
        self.records = records
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        margin_left = 60
        margin_bottom = 35
        margin_top = 20
        margin_right = 30

        chart_w = w - margin_left - margin_right
        chart_h = h - margin_top - margin_bottom

        # Background grid
        painter.setPen(QPen(QColor(45, 45, 45), 1, Qt.DashLine))
        for i in range(4):
            y = margin_top + (chart_h / 3) * i
            painter.drawLine(margin_left, y, w - margin_right, y)
            val = int(60 - (20 * i))
            painter.setPen(QPen(QColor(140, 140, 140)))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(margin_left - 35, y + 4, f"{val}m")
            painter.setPen(QPen(QColor(45, 45, 45), 1, Qt.DashLine))

        if not self.records:
            return

        bar_group_width = chart_w / len(self.records)
        bar_w = min(24, bar_group_width * 0.35)

        for i, rec in enumerate(self.records):
            center_x = margin_left + bar_group_width * (i + 0.5)

            # Idling bar (Yellow/Red)
            # max scale = 70 min
            idle_h = (rec.idling_time_min / 70.0) * chart_h
            idle_y = margin_top + chart_h - idle_h
            
            idle_color = QColor(239, 68, 68) if rec.idling_time_min >= 45 else QColor(255, 205, 17)
            painter.setBrush(QBrush(idle_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(center_x - bar_w - 2, idle_y, bar_w, idle_h, 3, 3)

            # Load cycles bar (Blue)
            # max scale = 15 cycles
            cycles_h = (rec.load_cycles / 15.0) * chart_h
            cycles_y = margin_top + chart_h - cycles_h
            painter.setBrush(QBrush(QColor(59, 130, 246)))
            painter.drawRoundedRect(center_x + 2, cycles_y, bar_w, cycles_h, 3, 3)

            # Value labels above bars
            painter.setPen(QPen(idle_color))
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.drawText(center_x - bar_w - 4, idle_y - 4, f"{rec.idling_time_min}m")

            painter.setPen(QPen(QColor(147, 197, 253)))
            painter.drawText(center_x + 3, cycles_y - 4, f"{rec.load_cycles}c")

            # Timestamp x label
            time_part = rec.timestamp.split(" ")[1][:5]
            date_part = rec.timestamp.split(" ")[0][5:]
            painter.setPen(QPen(QColor(180, 180, 180)))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(center_x - 22, h - 18, f"{date_part}")
            painter.drawText(center_x - 22, h - 5, f"{time_part}")


class TelemetryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.records = get_initial_telemetry()
        self._init_ui()
        self._populate_table()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Title Block
        title_row = QHBoxLayout()
        title = QLabel("TELEMETRY & MACHINE USAGE ANOMALY DETECTION (OUTCOME 4)")
        title.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {CAT_YELLOW}; letter-spacing: 0.5px;")
        title_row.addWidget(title)
        title_row.addStretch()

        btn_sim = QPushButton(" Ingest Simulated Live Ticker")
        btn_sim.setIcon(get_icon("zap", "#FFFFFF", 14))
        btn_sim.setProperty("class", "btn-secondary")
        btn_sim.clicked.connect(self._add_simulated_record)
        title_row.addWidget(btn_sim)
        main_layout.addLayout(title_row)

        subtitle = QLabel("Continuous automated surveillance for excessive idling, unfastened seatbelts, and irregular fuel-to-payload ratios.")
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; margin-top: -8px;")
        main_layout.addWidget(subtitle)

        # ---------------------------------------------
        # 1. ANOMALY DETECTION ALERT CARDS (3 CARDS)
        # ---------------------------------------------
        anomalies = evaluate_anomalies(self.records)
        anom_layout = QHBoxLayout()
        anom_layout.setSpacing(14)

        # Card 1: Excessive Idling
        card_idle = self._create_anomaly_card(
            title="EXCESSIVE IDLING DETECTED",
            value="55m & 60m Spikes",
            detail="Threshold: 45 min. Detected in rows 2 & 4. Significant fuel loss & carbon emissions.",
            action_text="Enable CAT AES (Auto Engine Shutdown)",
            border_color=STATUS_DANGER,
            bg_color="#301515",
            icon_name="alert-octagon"
        )
        anom_layout.addWidget(card_idle)

        # Card 2: Unsafe Operation Pattern
        card_safety = self._create_anomaly_card(
            title="UNSAFE USAGE PATTERN",
            value="Seatbelt Unfastened (2x)",
            detail="Engine active while seatbelt unfastened. Logged at 10:00:00 and 09:00:00.",
            action_text="Interlock Audio Alarm Triggered",
            border_color=STATUS_WARNING,
            bg_color="#2B200A",
            icon_name="alert-triangle"
        )
        anom_layout.addWidget(card_safety)

        # Card 3: Low Efficiency / Fuel Discrepancy
        card_eff = self._create_anomaly_card(
            title="EFFICIENCY DISCREPANCY",
            value="1-2 Cycles / Session",
            detail="High idling & fuel burn with minimal bucket load cycles. Indicates site staging blockage.",
            action_text="Check Haul Truck Dispatch Queue",
            border_color=STATUS_INFO,
            bg_color="#102030",
            icon_name="trending-down"
        )
        anom_layout.addWidget(card_eff)

        main_layout.addLayout(anom_layout)

        # ---------------------------------------------
        # 2. HISTORICAL TELEMETRY TABLE (IMAGE 2 DATA)
        # ---------------------------------------------
        table_header = QLabel("MACHINE USAGE LOG (FROM SPECIFICATION TABLE)")
        table_header.setStyleSheet("font-size: 13px; font-weight: bold; color: #FFFFFF; margin-top: 4px;")
        main_layout.addWidget(table_header)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Timestamp", "Machine ID", "Operator ID", "Engine Hours",
            "Fuel Used (L)", "Load Cycles", "Idling Time (min)",
            "Seatbelt Status", "Safety Alert Triggered"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMaximumHeight(180)
        main_layout.addWidget(self.table)

        # ---------------------------------------------
        # 3. VISUAL TELEMETRY CHARTS
        # ---------------------------------------------
        chart_card = QFrame()
        chart_card.setProperty("class", "cat-card")
        c_layout = QVBoxLayout(chart_card)
        c_layout.setContentsMargins(14, 10, 14, 10)
        c_layout.setSpacing(6)

        c_top = QHBoxLayout()
        c_title = QLabel("TELEMETRY PATTERN VISUALIZER: IDLING TIME (MIN) vs LOAD CYCLES")
        c_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #FFFFFF;")
        c_top.addWidget(c_title)
        c_top.addStretch()

        leg_idle = QLabel("■ Idling Time (Red if >= 45m)")
        leg_idle.setStyleSheet(f"color: {STATUS_DANGER}; font-size: 11px; font-weight: bold;")
        leg_cycles = QLabel("■ Load Cycles")
        leg_cycles.setStyleSheet("color: #60A5FA; font-size: 11px; font-weight: bold;")
        c_top.addWidget(leg_idle)
        c_top.addWidget(leg_cycles)
        c_layout.addLayout(c_top)

        self.chart_widget = TelemetryBarChart(self.records)
        c_layout.addWidget(self.chart_widget)

        main_layout.addWidget(chart_card)

    def _create_anomaly_card(self, title: str, value: str, detail: str, action_text: str, border_color: str, bg_color: str, icon_name: str = "alert-triangle") -> QFrame:
        card = QFrame()
        card_id = f"anomCard_{abs(hash(title)) % 10000}"
        card.setObjectName(card_id)
        card.setStyleSheet(f"""
            QFrame#{card_id} {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 12px;
            }}
            QFrame#{card_id} QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setSpacing(6)

        t_row = QHBoxLayout()
        t_row.setSpacing(6)
        ic_lbl = QLabel()
        ic_lbl.setPixmap(get_pixmap(icon_name, border_color, 16))
        t = QLabel(title)
        t.setStyleSheet(f"font-size: 11px; font-weight: 800; color: {border_color}; letter-spacing: 0.5px;")
        t_row.addWidget(ic_lbl)
        t_row.addWidget(t)
        t_row.addStretch()
        lay.addLayout(t_row)

        v = QLabel(value)
        v.setStyleSheet("font-size: 18px; font-weight: 900; color: #FFFFFF;")
        lay.addWidget(v)

        d = QLabel(detail)
        d.setStyleSheet(f"font-size: 11px; color: {TEXT_SECONDARY};")
        d.setWordWrap(True)
        lay.addWidget(d)

        act = QLabel(f"ACTION: {action_text}")
        act.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {CAT_YELLOW}; margin-top: 4px;")
        lay.addWidget(act)

        return card

    def _populate_table(self):
        self.table.setRowCount(len(self.records))
        for row, rec in enumerate(self.records):
            # Timestamp
            self.table.setItem(row, 0, QTableWidgetItem(rec.timestamp))
            # Machine ID
            self.table.setItem(row, 1, QTableWidgetItem(rec.machine_id))
            # Operator ID
            self.table.setItem(row, 2, QTableWidgetItem(rec.operator_id))
            # Engine Hours
            self.table.setItem(row, 3, QTableWidgetItem(f"{rec.engine_hours:.1f}"))
            # Fuel
            self.table.setItem(row, 4, QTableWidgetItem(f"{rec.fuel_used_l:.1f} L"))
            # Load cycles
            self.table.setItem(row, 5, QTableWidgetItem(str(rec.load_cycles)))

            # Idling Time
            idle_item = QTableWidgetItem(f"{rec.idling_time_min} min")
            if rec.idling_time_min >= 45:
                idle_item.setForeground(Qt.GlobalColor.red)
                idle_item.setFont(self._bold_font())
            self.table.setItem(row, 6, idle_item)

            # Seatbelt
            sb_item = QTableWidgetItem(rec.seatbelt_status)
            if rec.seatbelt_status.lower() == "unfastened":
                sb_item.setForeground(Qt.GlobalColor.red)
                sb_item.setFont(self._bold_font())
            else:
                sb_item.setForeground(Qt.GlobalColor.green)
            self.table.setItem(row, 7, sb_item)

            # Alert triggered
            alert_item = QTableWidgetItem(rec.safety_alert_triggered)
            alert_item.setTextAlignment(Qt.AlignCenter)
            if rec.safety_alert_triggered.lower() == "yes":
                alert_item.setForeground(Qt.GlobalColor.red)
                alert_item.setFont(self._bold_font())
            else:
                alert_item.setForeground(Qt.GlobalColor.lightGray)
            self.table.setItem(row, 8, alert_item)

    def _bold_font(self):
        f = self.font()
        f.setBold(True)
        return f

    def _add_simulated_record(self):
        new_rec = TelemetryRecord(
            timestamp="2025-05-02 11:30:00",
            machine_id="EXC001",
            operator_id="OP1001",
            engine_hours=1532.8,
            fuel_used_l=4.5,
            load_cycles=8,
            idling_time_min=20,
            seatbelt_status="Fastened",
            safety_alert_triggered="No"
        )
        self.records.append(new_rec)
        self._populate_table()
        self.chart_widget.set_records(self.records)
        QMessageBox.information(self, "Telemetry Feed Received", "Simulated IoT telemetry packet ingested: 8 load cycles, 20m idle, Seatbelt Fastened (Nominal).")
