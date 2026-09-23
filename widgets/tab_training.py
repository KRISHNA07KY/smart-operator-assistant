"""
Operator Training Hub Widget (Outcome 3)
Features:
1. Interactive In-Cab Excavator Simulation Drill (Kinematic boom/arm/bucket angle drill)
2. E-Learning Interactive Course Catalog (Video modules with progress)
3. 1-on-1 Certified CAT Instructor Coaching Booking
"""

import math
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSlider, QProgressBar, QComboBox, QDateEdit,
    QTextEdit, QDialog, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, QPointF, QDate
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from config import (
    CAT_YELLOW, CAT_BLACK, CAT_CARD_BG, CAT_BORDER, STATUS_SAFE,
    STATUS_WARNING, STATUS_DANGER, STATUS_INFO, TEXT_MUTED, TEXT_SECONDARY, TEXT_PRIMARY
)
from utils.icon_manager import get_icon, get_pixmap


class ExcavatorSimDrillWidget(QWidget):
    """
    2D interactive kinematics simulation widget for in-cab training.
    Operators practice boom height, arm reach, and bucket curl angle to hit safety targets.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 240)
        self.boom_angle = 35    # degrees from horizontal
        self.arm_angle = 70     # degrees relative to boom
        self.bucket_angle = 45  # degrees relative to arm

    def set_angles(self, boom, arm, bucket):
        self.boom_angle = boom
        self.arm_angle = arm
        self.bucket_angle = bucket
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Canvas background (Trench excavation pit visual)
        painter.fillRect(0, 0, w, h, QColor(22, 22, 22))

        # Ground line and trench pit
        ground_y = h - 60
        painter.setPen(QPen(QColor(80, 65, 45), 2))
        painter.setBrush(QBrush(QColor(55, 42, 28)))
        
        # Ground polygon
        trench_x1 = w * 0.45
        trench_x2 = w * 0.85
        trench_depth = ground_y + 40
        ground_poly = [
            QPointF(0, ground_y),
            QPointF(trench_x1, ground_y),
            QPointF(trench_x1 + 20, trench_depth),
            QPointF(trench_x2 - 20, trench_depth),
            QPointF(trench_x2, ground_y),
            QPointF(w, ground_y),
            QPointF(w, h),
            QPointF(0, h)
        ]
        painter.drawPolygon(ground_poly)

        # Target digging sweet spot marker
        target_center_x = (trench_x1 + trench_x2) / 2
        painter.setPen(QPen(QColor(16, 185, 129, 180), 2, Qt.DashLine))
        painter.drawEllipse(QPointF(target_center_x, trench_depth - 15), 18, 18)
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.setPen(QPen(QColor(16, 185, 129)))
        painter.drawText(target_center_x - 30, trench_depth + 18, "TARGET GRADE")

        # Excavator Base / Cab
        cab_x = 70
        cab_y = ground_y - 20
        # Tracks
        painter.setBrush(QBrush(QColor(40, 40, 40)))
        painter.setPen(QPen(Qt.black, 1.5))
        painter.drawRoundedRect(cab_x - 35, cab_y, 70, 20, 4, 4)

        # Cab body (CAT Yellow)
        painter.setBrush(QBrush(QColor(255, 205, 17)))
        painter.drawRoundedRect(cab_x - 25, cab_y - 35, 50, 35, 4, 4)
        
        # Cab window
        painter.setBrush(QBrush(QColor(100, 160, 220, 200)))
        painter.drawRect(cab_x + 5, cab_y - 30, 16, 20)

        # Pivot point (Boom base)
        pivot_x = cab_x + 15
        pivot_y = cab_y - 20

        # Kinematics: Boom
        boom_len = 75
        rad_boom = math.radians(-self.boom_angle)
        boom_tip_x = pivot_x + boom_len * math.cos(rad_boom)
        boom_tip_y = pivot_y + boom_len * math.sin(rad_boom)

        # Kinematics: Arm / Stick
        arm_len = 65
        rad_arm = rad_boom + math.radians(self.arm_angle)
        arm_tip_x = boom_tip_x + arm_len * math.cos(rad_arm)
        arm_tip_y = boom_tip_y + arm_len * math.sin(rad_arm)

        # Kinematics: Bucket
        bucket_len = 30
        rad_bucket = rad_arm + math.radians(self.bucket_angle)
        bucket_tip_x = arm_tip_x + bucket_len * math.cos(rad_bucket)
        bucket_tip_y = arm_tip_y + bucket_len * math.sin(rad_bucket)

        # Draw Boom Link
        painter.setPen(QPen(QColor(255, 205, 17), 8, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(pivot_x, pivot_y, boom_tip_x, boom_tip_y)

        # Draw Arm Link
        painter.setPen(QPen(QColor(240, 240, 240), 6, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(boom_tip_x, boom_tip_y, arm_tip_x, arm_tip_y)

        # Draw Bucket Link
        painter.setPen(QPen(QColor(50, 50, 50), 7, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(arm_tip_x, arm_tip_y, bucket_tip_x, bucket_tip_y)

        # Pivot joints (pins)
        painter.setBrush(QBrush(Qt.black))
        painter.setPen(QPen(Qt.white, 1.5))
        painter.drawEllipse(QPointF(pivot_x, pivot_y), 4, 4)
        painter.drawEllipse(QPointF(boom_tip_x, boom_tip_y), 4, 4)
        painter.drawEllipse(QPointF(arm_tip_x, arm_tip_y), 4, 4)


class TrainingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Title
        title = QLabel("OPERATOR TRAINING & SKILL ACCELERATION HUB (OUTCOME 3)")
        title.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {CAT_YELLOW}; letter-spacing: 0.5px;")
        main_layout.addWidget(title)

        subtitle = QLabel("Continuous learning modules: In-cab kinematic simulation drill, verified e-learning courses, and 1-on-1 certified instructor coaching.")
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; margin-top: -8px;")
        main_layout.addWidget(subtitle)

        # Top Row: Simulation Drill + E-learning Courses
        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        # ----------------------------------------------------
        # 1. INTERACTIVE MACHINE SIMULATION DRILL
        # ----------------------------------------------------
        sim_card = QFrame()
        sim_card.setProperty("class", "cat-card")
        sim_layout = QVBoxLayout(sim_card)
        sim_layout.setSpacing(10)

        sim_header = QHBoxLayout()
        sim_title = QLabel("1. INTERACTIVE EXCAVATOR KINEMATICS DRILL")
        sim_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {CAT_YELLOW};")
        sim_header.addWidget(sim_title)
        sim_header.addStretch()

        self.lbl_drill_score = QLabel("SCORE: 96 / 100 (PASSED)")
        self.lbl_drill_score.setFixedHeight(26)
        self.lbl_drill_score.setStyleSheet(f"""
            background-color: #152E1D;
            color: {STATUS_SAFE};
            border: 1px solid {STATUS_SAFE};
            border-radius: 4px;
            padding: 3px 10px;
            font-size: 11px;
            font-weight: bold;
        """)
        sim_header.addWidget(self.lbl_drill_score, alignment=Qt.AlignVCenter)
        sim_layout.addLayout(sim_header)

        # 2D Kinematics Canvas
        self.sim_canvas = ExcavatorSimDrillWidget()
        sim_layout.addWidget(self.sim_canvas)

        # Slider Controls
        ctrl_grid = QGridLayout()
        ctrl_grid.setSpacing(6)

        # Boom slider
        ctrl_grid.addWidget(QLabel("Boom Elevation:"), 0, 0)
        self.slider_boom = QSlider(Qt.Horizontal)
        self.slider_boom.setRange(10, 65)
        self.slider_boom.setValue(35)
        self.slider_boom.valueChanged.connect(self._on_sim_changed)
        ctrl_grid.addWidget(self.slider_boom, 0, 1)

        # Arm slider
        ctrl_grid.addWidget(QLabel("Arm / Stick Angle:"), 1, 0)
        self.slider_arm = QSlider(Qt.Horizontal)
        self.slider_arm.setRange(30, 110)
        self.slider_arm.setValue(70)
        self.slider_arm.valueChanged.connect(self._on_sim_changed)
        ctrl_grid.addWidget(self.slider_arm, 1, 1)

        # Bucket slider
        ctrl_grid.addWidget(QLabel("Bucket Curl:"), 2, 0)
        self.slider_bucket = QSlider(Qt.Horizontal)
        self.slider_bucket.setRange(10, 90)
        self.slider_bucket.setValue(45)
        self.slider_bucket.valueChanged.connect(self._on_sim_changed)
        ctrl_grid.addWidget(self.slider_bucket, 2, 1)

        sim_layout.addLayout(ctrl_grid)

        # Check alignment button
        btn_eval = QPushButton(" Evaluate Drill Target Alignment")
        btn_eval.setIcon(get_icon("target", "#000000", 14))
        btn_eval.setProperty("class", "btn-primary")
        btn_eval.clicked.connect(self._evaluate_drill)
        sim_layout.addWidget(btn_eval)

        top_row.addWidget(sim_card, stretch=5)

        # ----------------------------------------------------
        # 2. E-LEARNING VIDEO / COURSE CATALOG
        # ----------------------------------------------------
        course_card = QFrame()
        course_card.setProperty("class", "cat-card")
        course_layout = QVBoxLayout(course_card)
        course_layout.setSpacing(10)

        course_header = QLabel("2. CERTIFIED E-LEARNING VIDEO COURSES")
        course_header.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {CAT_YELLOW};")
        course_layout.addWidget(course_header)

        # Course items
        c1 = self._create_course_item(
            title="Next-Gen Excavator Safety & Blind Spots",
            duration="12 mins",
            progress=100,
            status_text="COMPLETED",
            status_color=STATUS_SAFE
        )
        c2 = self._create_course_item(
            title="Eco-Mode Idling Reduction & Fuel Savings",
            duration="18 mins",
            progress=65,
            status_text="IN PROGRESS (65%)",
            status_color=STATUS_WARNING
        )
        c3 = self._create_course_item(
            title="Trenching & Slope Stability in Heavy Rain",
            duration="25 mins",
            progress=0,
            status_text="NEW MODULE",
            status_color=STATUS_INFO
        )

        course_layout.addWidget(c1)
        course_layout.addWidget(c2)
        course_layout.addWidget(c3)
        course_layout.addStretch()

        top_row.addWidget(course_card, stretch=5)
        main_layout.addLayout(top_row)

        # ----------------------------------------------------
        # 3. 1-ON-1 INSTRUCTOR COACHING BOOKING
        # ----------------------------------------------------
        booking_card = QFrame()
        booking_card.setProperty("class", "cat-card")
        b_layout = QVBoxLayout(booking_card)
        b_layout.setSpacing(10)

        b_header = QLabel("3. INSTRUCTOR BOOKING — 1-ON-1 CERTIFIED CAT COACHING")
        b_header.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {CAT_YELLOW};")
        b_layout.addWidget(b_header)

        book_grid = QHBoxLayout()
        book_grid.setSpacing(14)

        # Col 1: Instructor
        col1 = QVBoxLayout()
        col1.addWidget(QLabel("Select Master Instructor:"))
        self.cb_instructor = QComboBox()
        self.cb_instructor.addItems([
            "Mike Vance — CAT Master Certified Trainer (15 yrs exp)",
            "Sarah Jenkins — Heavy Earthmoving & Safety Specialist",
            "Carlos Mendez — Trenching & Machine Efficiency Coach"
        ])
        col1.addWidget(self.cb_instructor)
        book_grid.addLayout(col1)

        # Col 2: Topic
        col2 = QVBoxLayout()
        col2.addWidget(QLabel("Skill Focus Area:"))
        self.cb_topic = QComboBox()
        self.cb_topic.addItems([
            "Excessive Idling Mitigation & AES Setup",
            "Trench Wall Collapse Prevention in Rain",
            "Bucket Cycle Speed & Fuel Optimization",
            "360° Proximity Hazard Navigation"
        ])
        col2.addWidget(self.cb_topic)
        book_grid.addLayout(col2)

        # Col 3: Date & Shift
        col3 = QVBoxLayout()
        col3.addWidget(QLabel("Preferred Date / Shift Slot:"))
        self.cb_shift = QComboBox()
        self.cb_shift.addItems([
            "Tomorrow — Morning Shift (08:00 - 09:00)",
            "Tomorrow — Afternoon Shift (13:00 - 14:00)",
            "Friday — Tailgate Safety Review (15:00)"
        ])
        col3.addWidget(self.cb_shift)
        book_grid.addLayout(col3)

        # Col 4: Button
        col4 = QVBoxLayout()
        col4.addWidget(QLabel("Action:"))
        btn_book = QPushButton(" Book 1-on-1 Session")
        btn_book.setIcon(get_icon("calendar", "#000000", 14))
        btn_book.setProperty("class", "btn-primary")
        btn_book.clicked.connect(self._book_session)
        col4.addWidget(btn_book)
        book_grid.addLayout(col4)

        b_layout.addLayout(book_grid)
        main_layout.addWidget(booking_card)

    def _create_course_item(self, title: str, duration: str, progress: int, status_text: str, status_color: str) -> QFrame:
        item_frame = QFrame()
        item_frame.setStyleSheet("background-color: #1A1A1A; border-radius: 6px; padding: 10px;")
        lay = QVBoxLayout(item_frame)
        lay.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(8)
        
        vid_icon = QLabel()
        vid_icon.setPixmap(get_pixmap("video", "#93C5FD", 14))
        top.addWidget(vid_icon)

        t = QLabel(title)
        t.setStyleSheet("font-weight: bold; font-size: 12px; color: #FFFFFF;")
        top.addWidget(t)
        top.addStretch()

        dur = QLabel(duration)
        dur.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        top.addWidget(dur)
        lay.addLayout(top)

        # Progress bar
        pbar = QProgressBar()
        pbar.setRange(0, 100)
        pbar.setValue(progress)
        pbar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #242424;
                border: 1px solid {CAT_BORDER};
                border-radius: 3px;
                height: 8px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {status_color};
            }}
        """)
        lay.addWidget(pbar)

        bot = QHBoxLayout()
        
        stat_box = QHBoxLayout()
        stat_box.setSpacing(4)
        if status_text == "COMPLETED":
            chk_icon = QLabel()
            chk_icon.setPixmap(get_pixmap("check-circle", status_color, 12))
            stat_box.addWidget(chk_icon)
        stat = QLabel(status_text)
        stat.setStyleSheet(f"color: {status_color}; font-size: 10px; font-weight: bold;")
        stat_box.addWidget(stat)
        bot.addLayout(stat_box)
        bot.addStretch()

        btn_launch = QPushButton(" Launch Player")
        btn_launch.setIcon(get_icon("play", "#FFFFFF", 11))
        btn_launch.setProperty("class", "btn-secondary")
        btn_launch.setStyleSheet("font-size: 11px; padding: 3px 8px;")
        btn_launch.clicked.connect(lambda: QMessageBox.information(self, "Course Player", f"Launching interactive in-cab module: '{title}'.\nProgress is automatically saved to operator profile OP1001."))
        bot.addWidget(btn_launch)
        lay.addLayout(bot)

        return item_frame

    def _on_sim_changed(self):
        b = self.slider_boom.value()
        a = self.slider_arm.value()
        k = self.slider_bucket.value()
        self.sim_canvas.set_angles(b, a, k)

    def _evaluate_drill(self):
        b = self.slider_boom.value()
        a = self.slider_arm.value()
        k = self.slider_bucket.value()

        # Target range: boom ~30-40, arm ~65-75, bucket ~40-50
        diff = abs(b - 35) + abs(a - 70) + abs(k - 45)
        score = max(50, 100 - diff * 2)

        if score >= 85:
            self.lbl_drill_score.setText(f"SCORE: {score} / 100 (PASSED ✔)")
            self.lbl_drill_score.setStyleSheet(f"background-color: #152E1D; color: {STATUS_SAFE}; border: 1px solid {STATUS_SAFE}; border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: bold;")
            QMessageBox.information(self, "Drill Completed", f"Excellent Job! Bucket tooth attack angle is optimal ({score}% precision). Zero sidewall trench shearing detected.")
        else:
            self.lbl_drill_score.setText(f"SCORE: {score} / 100 (NEEDS ADJUSTMENT)")
            self.lbl_drill_score.setStyleSheet(f"background-color: #382405; color: {STATUS_WARNING}; border: 1px solid {STATUS_WARNING}; border-radius: 4px; padding: 3px 8px; font-size: 11px; font-weight: bold;")
            QMessageBox.warning(self, "Drill Feedback", f"Score: {score}%. Bucket angle is too steep or shallow. Align bucket teeth parallel to trench pit floor (Target: ~45°).")

    def _book_session(self):
        inst = self.cb_instructor.currentText().split("—")[0].strip()
        topic = self.cb_topic.currentText()
        shift = self.cb_shift.currentText()
        QMessageBox.information(self, "Coaching Session Confirmed", f"1-on-1 Session Booked!\n\nInstructor: {inst}\nTopic: {topic}\nSlot: {shift}\n\nCalendar invite and telemetry pre-brief sent to instructor.")
