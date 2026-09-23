"""
Smoke tests for CAT Smart Operator Assistant Dashboard
Verifies data models, dummy ML prediction hook, and Qt UI instantiation.
"""

import sys
import os

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.dummy_tasks import get_initial_tasks
from models.dummy_ml import predict_task_time, TaskTimeInput
from models.dummy_telemetry import get_initial_telemetry, evaluate_anomalies
from models.dummy_incident import get_initial_incidents

def test_tasks_model():
    tasks = get_initial_tasks()
    assert len(tasks) == 5, f"Expected 5 tasks, got {len(tasks)}"
    assert tasks[0].task_id == "T001"
    assert tasks[1].task_id == "T002"
    print("[OK] Tasks model passed.")

def test_ml_prediction():
    inp = TaskTimeInput(
        task_type="Trenching",
        weather="Rainy",
        operator_skill="Intermediate",
        machine_age=4
    )
    res = predict_task_time(inp)
    assert res.predicted_minutes > 0
    assert res.baseline_minutes == 45
    assert len(res.factor_impacts) == 3
    assert len(res.ai_recommendations) > 0
    print(f"[OK] ML prediction passed: predicted={res.predicted_minutes}m, baseline={res.baseline_minutes}m")

def test_telemetry_and_anomalies():
    records = get_initial_telemetry()
    assert len(records) == 4, f"Expected 4 telemetry records, got {len(records)}"
    anomalies = evaluate_anomalies(records)
    assert len(anomalies) >= 2, "Expected excessive idling and seatbelt anomalies"
    print(f"[OK] Telemetry and anomaly detection passed: {len(anomalies)} anomalies detected.")

def test_qt_ui():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtWidgets import QApplication
    from main import MainWindow
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        
    window = MainWindow()
    assert window is not None
    assert window.tab_tasks is not None
    assert window.tab_safety is not None
    assert window.tab_estimator is not None
    assert window.tab_telemetry is not None
    assert window.tab_training is not None
    
    # Test tab switching
    for idx in range(5):
        window.stack.setCurrentIndex(idx)
        assert window.stack.currentIndex() == idx

    print("[OK] Qt UI instantiation and tab switching passed.")

if __name__ == "__main__":
    test_tasks_model()
    test_ml_prediction()
    test_telemetry_and_anomalies()
    test_qt_ui()
    print("\nALL SMOKE TESTS COMPLETED SUCCESSFULLY!")
