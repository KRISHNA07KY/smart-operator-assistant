"""
Daily Task Dashboard Widget (Outcome 1)
Displays scheduled tasks for the day, active task countdown, KPI cards, and task management.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QProgressBar, QDialog, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from config import (
    CAT_YELLOW, CAT_CARD_BG, CAT_BORDER, STATUS_SAFE, STATUS_WARNING,
    STATUS_DANGER, STATUS_INFO, TEXT_MUTED, TEXT_SECONDARY, TEXT_PRIMARY
)
from utils.icon_manager import get_icon, get_pixmap
from models.dummy_tasks import get_initial_tasks, TaskItem

class TasksTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = get_initial_tasks()
        self.active_task = self.tasks[1]  # T002 Trenching is default active
        self._init_ui()
        self._populate_table()
        self._update_kpis()

        # Timer to tick active task progress
        self.tick_timer = QTimer(self)
        self.tick_timer.timeout.connect(self._on_tick)
        self.tick_timer.start(2000)  # every 2 seconds advance simulation

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(18)

        # 1. Page Title & Action Bar
        title_layout = QHBoxLayout()
        header_title = QLabel("DAILY TASK DISPATCH & SCHEDULE")
        header_title.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {CAT_YELLOW}; letter-spacing: 0.5px;")
        title_layout.addWidget(header_title)
        
        title_layout.addStretch()

        btn_add_task = QPushButton(" SCHEDULE NEW TASK")
        btn_add_task.setIcon(get_icon("tasks", "#000000", 16))
        btn_add_task.setProperty("class", "btn-primary")
        btn_add_task.clicked.connect(self._open_add_task_dialog)
        title_layout.addWidget(btn_add_task)
        main_layout.addLayout(title_layout)

        # 2. KPI Summary Cards
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(14)
        
        self.card_total = self._create_kpi_card("TOTAL TASKS", "5", "Scheduled for shift", CAT_YELLOW)
        self.card_progress = self._create_kpi_card("IN PROGRESS", "1", "Active operation", STATUS_WARNING)
        self.card_completed = self._create_kpi_card("COMPLETED", "1", "Successfully logged", STATUS_SAFE)
        self.card_efficiency = self._create_kpi_card("SHIFT EFFICIENCY", "94%", "On-schedule rate", STATUS_INFO)

        kpi_layout.addWidget(self.card_total)
        kpi_layout.addWidget(self.card_progress)
        kpi_layout.addWidget(self.card_completed)
        kpi_layout.addWidget(self.card_efficiency)
        main_layout.addLayout(kpi_layout)

        # 3. Active Task Live Hero Card
        self.hero_card = QFrame()
        self.hero_card.setObjectName("heroCard")
        self.hero_card.setStyleSheet(f"""
            QFrame#heroCard {{
                background-color: #211E14;
                border: 2px solid {CAT_YELLOW};
                border-radius: 10px;
                padding: 14px;
            }}
            QFrame#heroCard QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        hero_layout = QVBoxLayout(self.hero_card)
        hero_layout.setSpacing(10)

        hero_top = QHBoxLayout()
        self.hero_badge = QLabel("● CURRENT ACTIVE TASK")
        self.hero_badge.setStyleSheet(f"color: {CAT_YELLOW}; font-weight: bold; font-size: 11px; letter-spacing: 1px;")
        hero_top.addWidget(self.hero_badge)
        
        hero_top.addStretch()

        self.hero_time_label = QLabel("Elapsed: 28 min / Target: 45 min")
        self.hero_time_label.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: bold;")
        hero_top.addWidget(self.hero_time_label)
        hero_layout.addLayout(hero_top)

        hero_mid = QHBoxLayout()
        self.hero_task_name = QLabel("T002: Trenching — Foundation Zone B")
        self.hero_task_name.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        hero_mid.addWidget(self.hero_task_name)
        hero_mid.addStretch()

        # Context badges with vector icons
        self.badge_weather = self._create_badge("cloud-rain", "#93C5FD", "Weather: Rainy", "#1E293B")
        self.badge_skill = self._create_badge("user", "#C7D2FE", "Operator: Intermediate", "#312E81")
        self.badge_age = self._create_badge("truck", "#F3F4F6", "Machine Age: 4 yrs", "#374151")

        hero_mid.addWidget(self.badge_weather)
        hero_mid.addWidget(self.badge_skill)
        hero_mid.addWidget(self.badge_age)
        hero_layout.addLayout(hero_mid)

        # Progress bar
        self.hero_progress = QProgressBar()
        self.hero_progress.setRange(0, 100)
        self.hero_progress.setValue(62)
        self.hero_progress.setTextVisible(True)
        self.hero_progress.setFormat("%p% Completed (On Track)")
        hero_layout.addWidget(self.hero_progress)

        # Action Buttons
        hero_actions = QHBoxLayout()
        hero_actions.addStretch()
        
        self.btn_pause = QPushButton(" Pause Task")
        self.btn_pause.setIcon(get_icon("pause", "#FFFFFF", 14))
        self.btn_pause.setProperty("class", "btn-secondary")
        self.btn_pause.clicked.connect(self._toggle_pause)
        hero_actions.addWidget(self.btn_pause)

        self.btn_complete = QPushButton(" Complete Task")
        self.btn_complete.setIcon(get_icon("check-circle", "#000000", 14))
        self.btn_complete.setProperty("class", "btn-primary")
        self.btn_complete.clicked.connect(self._complete_active_task)
        hero_actions.addWidget(self.btn_complete)

        self.btn_delay = QPushButton(" Report Weather Delay")
        self.btn_delay.setIcon(get_icon("alert-triangle", "#FFFFFF", 14))
        self.btn_delay.setProperty("class", "btn-secondary")
        self.btn_delay.clicked.connect(self._report_delay)
        hero_actions.addWidget(self.btn_delay)
        
        hero_layout.addLayout(hero_actions)
        main_layout.addWidget(self.hero_card)

        # 4. Scheduled Tasks Table Title
        table_title = QLabel("SCHEDULED SHIFT TASKS (FROM SPECIFICATION)")
        table_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF; margin-top: 4px;")
        main_layout.addWidget(table_title)

        # 5. Scheduled Tasks Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Task ID", "Task Type", "Weather", "Operator Skill",
            "Machine Age (yrs)", "Estimated Time", "Actual Time", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellDoubleClicked.connect(self._on_table_row_activated)
        main_layout.addWidget(self.table)

    def _create_kpi_card(self, title: str, value: str, subtext: str, color: str) -> QFrame:
        card = QFrame()
        card.setProperty("class", "cat-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        t = QLabel(title)
        t.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {TEXT_MUTED}; letter-spacing: 0.5px;")
        layout.addWidget(t)

        v = QLabel(value)
        v.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {color};")
        layout.addWidget(v)
        card.value_label = v

        s = QLabel(subtext)
        s.setStyleSheet(f"font-size: 11px; color: {TEXT_SECONDARY};")
        layout.addWidget(s)

        return card

    def _populate_table(self):
        self.table.setRowCount(len(self.tasks))
        for row, task in enumerate(self.tasks):
            # Task ID
            id_item = QTableWidgetItem(task.task_id)
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setFont(self._bold_font())
            self.table.setItem(row, 0, id_item)

            # Task Type
            type_item = QTableWidgetItem(task.task_type)
            type_item.setFont(self._bold_font())
            self.table.setItem(row, 1, type_item)

            # Weather
            weather_item = QTableWidgetItem(task.weather)
            weather_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, weather_item)

            # Operator Skill
            skill_item = QTableWidgetItem(task.operator_skill)
            skill_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, skill_item)

            # Machine Age
            age_item = QTableWidgetItem(f"{task.machine_age} yrs")
            age_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, age_item)

            # Estimated Time
            est_item = QTableWidgetItem(f"{task.estimated_time} min")
            est_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, est_item)

            # Actual Time
            act_text = f"{task.actual_time} min" if task.actual_time is not None else (f"{task.elapsed_time} min (active)" if task.status == "In Progress" else "-")
            act_item = QTableWidgetItem(act_text)
            act_item.setTextAlignment(Qt.AlignCenter)
            if task.actual_time and task.actual_time > task.estimated_time:
                act_item.setForeground(Qt.GlobalColor.red)
            elif task.actual_time and task.actual_time <= task.estimated_time:
                act_item.setForeground(Qt.GlobalColor.green)
            self.table.setItem(row, 6, act_item)

            # Status pill
            status_item = QTableWidgetItem(task.status)
            status_item.setTextAlignment(Qt.AlignCenter)
            if task.status == "Completed":
                status_item.setForeground(Qt.GlobalColor.green)
            elif task.status == "In Progress":
                status_item.setForeground(Qt.GlobalColor.yellow)
            else:
                status_item.setForeground(Qt.GlobalColor.lightGray)
            self.table.setItem(row, 7, status_item)

    def _bold_font(self):
        f = self.font()
        f.setBold(True)
        return f

    def _update_kpis(self):
        total = len(self.tasks)
        in_prog = sum(1 for t in self.tasks if t.status == "In Progress")
        comp = sum(1 for t in self.tasks if t.status == "Completed")
        self.card_total.value_label.setText(str(total))
        self.card_progress.value_label.setText(str(in_prog))
        self.card_completed.value_label.setText(str(comp))

    def _on_tick(self):
        if self.active_task and self.active_task.status == "In Progress":
            self.active_task.elapsed_time += 1
            est = self.active_task.estimated_time
            pct = min(100, int((self.active_task.elapsed_time / est) * 100))
            self.hero_progress.setValue(pct)
            self.hero_time_label.setText(f"Elapsed: {self.active_task.elapsed_time} min / Target: {est} min")
            if self.active_task.elapsed_time > est:
                self.hero_progress.setFormat(f"%p% Completed ({self.active_task.elapsed_time - est}m Delay)")
            else:
                self.hero_progress.setFormat("%p% Completed (On Track)")
            self._populate_table()

    def _create_badge(self, icon_name: str, icon_color: str, text: str, bg_color: str) -> QFrame:
        badge = QFrame()
        badge.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 4px;
            }}
            QFrame QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        lay = QHBoxLayout(badge)
        lay.setContentsMargins(6, 3, 6, 3)
        lay.setSpacing(6)
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_pixmap(icon_name, icon_color, 14))
        lay.addWidget(icon_lbl)
        
        text_lbl = QLabel(text)
        text_lbl.setStyleSheet(f"color: {icon_color}; font-size: 12px; font-weight: bold;")
        lay.addWidget(text_lbl)
        badge.text_lbl = text_lbl
        badge.icon_lbl = icon_lbl
        return badge

    def _toggle_pause(self):
        if self.tick_timer.isActive():
            self.tick_timer.stop()
            self.btn_pause.setIcon(get_icon("play", "#FFFFFF", 14))
            self.btn_pause.setText(" Resume Task")
        else:
            self.tick_timer.start(2000)
            self.btn_pause.setIcon(get_icon("pause", "#FFFFFF", 14))
            self.btn_pause.setText(" Pause Task")

    def _complete_active_task(self):
        if self.active_task:
            self.active_task.status = "Completed"
            self.active_task.actual_time = self.active_task.elapsed_time
            QMessageBox.information(self, "Task Completed", f"Task {self.active_task.task_id} ({self.active_task.task_type}) marked as Completed in {self.active_task.actual_time} minutes.")
            
            # Switch next pending to active
            for t in self.tasks:
                if t.status == "Pending":
                    t.status = "In Progress"
                    self.active_task = t
                    self.hero_task_name.setText(f"{t.task_id}: {t.task_type}")
                    self.badge_weather.text_lbl.setText(f"Weather: {t.weather}")
                    self.badge_skill.text_lbl.setText(f"Operator: {t.operator_skill}")
                    self.badge_age.text_lbl.setText(f"Machine Age: {t.machine_age} yrs")
                    break
            self._populate_table()
            self._update_kpis()

    def _report_delay(self):
        QMessageBox.warning(self, "Weather Delay Logged", "Adverse weather delay of +10 minutes logged to site supervisor. Estimated schedule adjusted.")
        if self.active_task:
            self.active_task.estimated_time += 10
            self.hero_time_label.setText(f"Elapsed: {self.active_task.elapsed_time} min / Target: {self.active_task.estimated_time} min")
            self._populate_table()

    def _on_table_row_activated(self, row, col):
        selected_task = self.tasks[row]
        self.active_task = selected_task
        self.hero_task_name.setText(f"{selected_task.task_id}: {selected_task.task_type}")
        self.badge_weather.text_lbl.setText(f"Weather: {selected_task.weather}")
        self.badge_skill.text_lbl.setText(f"Operator: {selected_task.operator_skill}")
        self.badge_age.text_lbl.setText(f"Machine Age: {selected_task.machine_age} yrs")
        self.hero_time_label.setText(f"Elapsed: {selected_task.elapsed_time} min / Target: {selected_task.estimated_time} min")

    def _open_add_task_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Schedule New Task")
        dialog.setFixedWidth(400)
        dialog.setStyleSheet("background-color: #242424; color: white;")
        layout = QVBoxLayout(dialog)

        form = QFormLayout()
        tid = QLineEdit(f"T00{len(self.tasks)+1}")
        ttype = QComboBox()
        ttype.addItems(["Earth Excavation", "Trenching", "Material Loading", "Grading", "Demolition", "Compaction"])
        
        weather = QComboBox()
        weather.addItems(["Sunny", "Rainy", "Cloudy", "Windy", "Stormy"])
        
        skill = QComboBox()
        skill.addItems(["Beginner", "Intermediate", "Expert"])
        
        age = QSpinBox()
        age.setRange(1, 15)
        age.setValue(3)

        est_time = QSpinBox()
        est_time.setRange(10, 300)
        est_time.setValue(45)

        form.addRow("Task ID:", tid)
        form.addRow("Task Type:", ttype)
        form.addRow("Weather:", weather)
        form.addRow("Operator Skill:", skill)
        form.addRow("Machine Age (yrs):", age)
        form.addRow("Estimated Time (min):", est_time)
        layout.addLayout(form)

        btn_save = QPushButton("Save & Add to Shift Schedule")
        btn_save.setProperty("class", "btn-primary")
        
        def save():
            new_task = TaskItem(
                task_id=tid.text().strip(),
                task_type=ttype.currentText(),
                weather=weather.currentText(),
                operator_skill=skill.currentText(),
                machine_age=age.value(),
                estimated_time=est_time.value(),
                actual_time=None,
                status="Pending"
            )
            self.tasks.append(new_task)
            self._populate_table()
            self._update_kpis()
            dialog.accept()

        btn_save.clicked.connect(save)
        layout.addWidget(btn_save)
        dialog.exec()
