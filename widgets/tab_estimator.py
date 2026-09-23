"""
Task Time Estimation Widget (Outcome 5 - ML Model Output Interface)
Allows operators/dispatchers to input task parameters and see the predicted
completion time, variance, confidence, factor impact breakdown, and AI recommendations.
Backed by the clean `models.dummy_ml.predict_task_time` hook.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QSlider, QProgressBar, QGridLayout,
    QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from config import (
    CAT_YELLOW, CAT_BLACK, CAT_CARD_BG, CAT_BORDER, STATUS_SAFE,
    STATUS_WARNING, STATUS_DANGER, STATUS_INFO, TEXT_MUTED, TEXT_SECONDARY, TEXT_PRIMARY
)
from utils.icon_manager import get_icon, get_pixmap
from models.dummy_ml import predict_task_time, TaskTimeInput, MLPredictionResult

class EstimatorTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._run_prediction()  # Initial calculation

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(18)

        # Title Block
        title = QLabel("AI TASK TIME ESTIMATOR (MACHINE LEARNING INTERFACE)")
        title.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {CAT_YELLOW}; letter-spacing: 0.5px;")
        main_layout.addWidget(title)

        subtitle = QLabel("Predict completion duration based on historical machine data, operator skill curve, machine age, and weather conditions.")
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; margin-top: -8px;")
        main_layout.addWidget(subtitle)

        # Main Split: Left = Input Controls, Right = ML Output Cards
        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)

        # ---------------------------------------------
        # LEFT: TASK PARAMETERS INPUT PANEL
        # ---------------------------------------------
        input_card = QFrame()
        input_card.setProperty("class", "cat-card")
        input_card.setMinimumWidth(380)
        input_card.setMaximumWidth(440)
        in_layout = QVBoxLayout(input_card)
        in_layout.setSpacing(14)

        in_header = QLabel("INPUT TASK PARAMETERS")
        in_header.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {CAT_YELLOW};")
        in_layout.addWidget(in_header)

        # 1. Task Type
        in_layout.addWidget(QLabel("Task Type:"))
        self.cb_task_type = QComboBox()
        self.cb_task_type.addItems([
            "Earth Excavation",
            "Trenching",
            "Material Loading",
            "Grading",
            "Demolition"
        ])
        self.cb_task_type.setCurrentText("Trenching")
        self.cb_task_type.currentIndexChanged.connect(self._run_prediction)
        in_layout.addWidget(self.cb_task_type)

        # 2. Weather Condition
        in_layout.addWidget(QLabel("Environmental Weather:"))
        self.cb_weather = QComboBox()
        self.cb_weather.addItems(["Sunny", "Cloudy", "Windy", "Rainy", "Stormy"])
        self.cb_weather.setCurrentText("Rainy")
        self.cb_weather.currentIndexChanged.connect(self._run_prediction)
        in_layout.addWidget(self.cb_weather)

        # 3. Operator Skill
        in_layout.addWidget(QLabel("Operator Skill Level:"))
        self.cb_skill = QComboBox()
        self.cb_skill.addItems(["Beginner", "Intermediate", "Expert"])
        self.cb_skill.setCurrentText("Intermediate")
        self.cb_skill.currentIndexChanged.connect(self._run_prediction)
        in_layout.addWidget(self.cb_skill)

        # 4. Machine Age (Years)
        age_label_row = QHBoxLayout()
        age_label_row.addWidget(QLabel("Machine Age:"))
        self.lbl_age_value = QLabel("4 Years")
        self.lbl_age_value.setStyleSheet(f"font-weight: bold; color: {CAT_YELLOW};")
        age_label_row.addWidget(self.lbl_age_value, alignment=Qt.AlignRight)
        in_layout.addLayout(age_label_row)

        self.slider_age = QSlider(Qt.Horizontal)
        self.slider_age.setRange(1, 10)
        self.slider_age.setValue(4)
        self.slider_age.valueChanged.connect(self._on_age_changed)
        in_layout.addWidget(self.slider_age)

        # Quick Presets from Image 1
        in_layout.addWidget(QLabel("Load Presets from Image 1:"))
        preset_layout = QGridLayout()
        preset_layout.setSpacing(6)

        btn_t1 = QPushButton("T001 (Excavation)")
        btn_t1.setProperty("class", "btn-secondary")
        btn_t1.clicked.connect(lambda: self._load_preset("Earth Excavation", "Sunny", "Expert", 2))

        btn_t2 = QPushButton("T002 (Trenching)")
        btn_t2.setProperty("class", "btn-secondary")
        btn_t2.clicked.connect(lambda: self._load_preset("Trenching", "Rainy", "Intermediate", 4))

        btn_t3 = QPushButton("T003 (Loading)")
        btn_t3.setProperty("class", "btn-secondary")
        btn_t3.clicked.connect(lambda: self._load_preset("Material Loading", "Cloudy", "Beginner", 3))

        btn_t5 = QPushButton("T005 (Demolition)")
        btn_t5.setProperty("class", "btn-secondary")
        btn_t5.clicked.connect(lambda: self._load_preset("Demolition", "Windy", "Intermediate", 6))

        preset_layout.addWidget(btn_t1, 0, 0)
        preset_layout.addWidget(btn_t2, 0, 1)
        preset_layout.addWidget(btn_t3, 1, 0)
        preset_layout.addWidget(btn_t5, 1, 1)
        in_layout.addLayout(preset_layout)

        in_layout.addStretch()

        # Run AI Button
        self.btn_predict = QPushButton(" RUN AI MODEL PREDICTION")
        self.btn_predict.setIcon(get_icon("zap", "#000000", 16))
        self.btn_predict.setProperty("class", "btn-primary")
        self.btn_predict.clicked.connect(self._run_prediction)
        in_layout.addWidget(self.btn_predict)

        split_layout.addWidget(input_card)

        # ---------------------------------------------
        # RIGHT: ML OUTPUT PRESENTATION CARDS
        # ---------------------------------------------
        out_container = QWidget()
        out_layout = QVBoxLayout(out_container)
        out_layout.setContentsMargins(0, 0, 0, 0)
        out_layout.setSpacing(14)

        # 1. Hero KPI Prediction Card
        self.pred_hero_card = QFrame()
        self.pred_hero_card.setObjectName("predHeroCard")
        self.pred_hero_card.setStyleSheet(f"""
            QFrame#predHeroCard {{
                background-color: #1F1C12;
                border: 2px solid {CAT_YELLOW};
                border-radius: 10px;
                padding: 14px;
            }}
            QFrame#predHeroCard QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        hero_layout = QVBoxLayout(self.pred_hero_card)

        hero_top = QHBoxLayout()
        hero_title = QLabel("AI ESTIMATED DURATION (ML OUTPUT)")
        hero_title.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {CAT_YELLOW}; letter-spacing: 0.5px;")
        hero_top.addWidget(hero_title)
        hero_top.addStretch()

        self.conf_badge = QLabel("92% MODEL CONFIDENCE")
        self.conf_badge.setStyleSheet(f"""
            background-color: #152E1D;
            color: {STATUS_SAFE};
            border: 1px solid {STATUS_SAFE};
            border-radius: 10px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: bold;
        """)
        hero_top.addWidget(self.conf_badge)
        hero_layout.addLayout(hero_top)

        # Big Predicted Minutes Number & Variance
        pred_num_row = QHBoxLayout()
        pred_num_row.setSpacing(20)

        self.lbl_predicted_time = QLabel("52 MIN")
        self.lbl_predicted_time.setStyleSheet(f"font-size: 44px; font-weight: 900; color: #FFFFFF;")
        pred_num_row.addWidget(self.lbl_predicted_time)

        # Benchmark Comparison Sub-block
        comp_layout = QVBoxLayout()
        comp_layout.setSpacing(2)
        
        self.lbl_baseline_time = QLabel("Standard Baseline: 45 min")
        self.lbl_baseline_time.setStyleSheet(f"font-size: 13px; color: {TEXT_MUTED};")
        comp_layout.addWidget(self.lbl_baseline_time)

        self.lbl_variance = QLabel("+7 min (+15.6% Expected Delay)")
        self.lbl_variance.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {STATUS_WARNING};")
        comp_layout.addWidget(self.lbl_variance)

        pred_num_row.addLayout(comp_layout)
        pred_num_row.addStretch()
        hero_layout.addLayout(pred_num_row)

        out_layout.addWidget(self.pred_hero_card)

        # 2. Factor Impact Breakdown Card
        factor_card = QFrame()
        factor_card.setProperty("class", "cat-card")
        f_layout = QVBoxLayout(factor_card)
        f_layout.setSpacing(10)

        f_header = QLabel("FEATURE IMPACT BREAKDOWN (AI DRIVERS)")
        f_header.setStyleSheet("font-size: 12px; font-weight: bold; color: #FFFFFF;")
        f_layout.addWidget(f_header)

        # Factor bars container
        self.factors_layout = QVBoxLayout()
        self.factors_layout.setSpacing(8)
        f_layout.addLayout(self.factors_layout)
        out_layout.addWidget(factor_card)

        # 3. AI Smart In-Cab Recommendations Card
        recs_card = QFrame()
        recs_card.setProperty("class", "cat-card")
        r_layout = QVBoxLayout(recs_card)
        r_layout.setSpacing(8)

        r_header_box = QHBoxLayout()
        r_icon = QLabel()
        r_icon.setPixmap(get_pixmap("lightbulb", CAT_YELLOW, 16))
        r_header = QLabel("IN-CAB AI EFFICIENCY & SAFETY ADVISORY")
        r_header.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {CAT_YELLOW};")
        r_header_box.addWidget(r_icon)
        r_header_box.addWidget(r_header)
        r_header_box.addStretch()
        r_layout.addLayout(r_header_box)

        self.recs_container = QVBoxLayout()
        self.recs_container.setSpacing(6)
        r_layout.addLayout(self.recs_container)

        out_layout.addWidget(recs_card)
        split_layout.addWidget(out_container, stretch=1)

        main_layout.addLayout(split_layout)

    def _on_age_changed(self, value):
        self.lbl_age_value.setText(f"{value} Years")
        self._run_prediction()

    def _load_preset(self, ttype, weather, skill, age):
        self.cb_task_type.setCurrentText(ttype)
        self.cb_weather.setCurrentText(weather)
        self.cb_skill.setCurrentText(skill)
        self.slider_age.setValue(age)
        self._run_prediction()

    def _run_prediction(self):
        task_input = TaskTimeInput(
            task_type=self.cb_task_type.currentText(),
            weather=self.cb_weather.currentText(),
            operator_skill=self.cb_skill.currentText(),
            machine_age=self.slider_age.value()
        )
        result: MLPredictionResult = predict_task_time(task_input)

        # Update hero metrics
        self.lbl_predicted_time.setText(f"{result.predicted_minutes} MIN")
        self.lbl_baseline_time.setText(f"Standard Baseline: {result.baseline_minutes} min")
        
        sign = "+" if result.variance_minutes > 0 else ""
        color = STATUS_WARNING if result.variance_minutes > 0 else (STATUS_SAFE if result.variance_minutes < 0 else TEXT_MUTED)
        self.lbl_variance.setText(f"{sign}{result.variance_minutes} min ({sign}{result.variance_pct}% Variance)")
        self.lbl_variance.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color};")
        
        self.conf_badge.setText(f"{result.confidence_score}% MODEL CONFIDENCE")

        # Clear and rebuild factor bars
        while self.factors_layout.count():
            item = self.factors_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for factor in result.factor_impacts:
            row_frame = QFrame()
            row_frame.setStyleSheet("background-color: #1A1A1A; border-radius: 4px; padding: 8px;")
            r_lay = QVBoxLayout(row_frame)
            r_lay.setContentsMargins(8, 4, 8, 4)
            r_lay.setSpacing(4)

            top = QHBoxLayout()
            name_lbl = QLabel(factor.factor_name)
            name_lbl.setStyleSheet("font-weight: bold; font-size: 12px; color: #FFFFFF;")
            
            f_sign = "+" if factor.impact_pct > 0 else ""
            f_color = STATUS_WARNING if factor.impact_pct > 0 else (STATUS_SAFE if factor.impact_pct < 0 else TEXT_MUTED)
            val_lbl = QLabel(f"{f_sign}{factor.impact_pct}%")
            val_lbl.setStyleSheet(f"font-weight: 800; font-size: 12px; color: {f_color};")
            top.addWidget(name_lbl)
            top.addStretch()
            top.addWidget(val_lbl)
            r_lay.addLayout(top)

            desc_lbl = QLabel(factor.description)
            desc_lbl.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED};")
            r_lay.addWidget(desc_lbl)

            self.factors_layout.addWidget(row_frame)

        # Clear and rebuild recommendations
        while self.recs_container.count():
            item = self.recs_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for rec in result.ai_recommendations:
            rec_frame = QFrame()
            rec_frame.setStyleSheet("background-color: #262417; border-left: 3px solid #FFCD11; border-radius: 2px;")
            r_box = QHBoxLayout(rec_frame)
            r_box.setContentsMargins(10, 6, 10, 6)
            r_box.setSpacing(8)

            ic_name = "lightbulb"
            ic_color = CAT_YELLOW
            if "Warning" in rec:
                ic_name = "alert-triangle"
                ic_color = STATUS_WARNING
            elif "Hydraulic" in rec:
                ic_name = "wrench"
                ic_color = STATUS_INFO
            elif "Optimal" in rec:
                ic_name = "check-circle"
                ic_color = STATUS_SAFE

            icon_lbl = QLabel()
            icon_lbl.setPixmap(get_pixmap(ic_name, ic_color, 14))
            r_box.addWidget(icon_lbl)

            rec_lbl = QLabel(rec)
            rec_lbl.setStyleSheet("font-size: 12px; color: #FFFFFF;")
            rec_lbl.setWordWrap(True)
            r_box.addWidget(rec_lbl, stretch=1)

            self.recs_container.addWidget(rec_frame)
