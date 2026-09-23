"""backend/bridge.py
QtWebChannel bridge exposing Python slots & signals to the frontend.
Enables bi-directional communication between JavaScript and Python Qt.
"""
import json
from PySide6.QtCore import QObject, Slot, Signal
from backend.dummy_ml import predict_safety, predict_task_time, detect_anomalies


class CatBridge(QObject):
    # Signals sent from Python to JS
    telemetryUpdated = Signal(str)
    alertTriggered = Signal(str)
    
    # Signal emitted when incident is logged locally
    incidentLogged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str, result=str)
    def predictSafety(self, inputs_json: str) -> str:
        """Invoked from JS to get safety prediction from Python ML backend."""
        try:
            data = json.loads(inputs_json)
        except Exception:
            data = {}
        res = predict_safety(data.get("inputs", data), data.get("context"))
        return json.dumps(res)

    @Slot(str, result=str)
    def predictTaskTime(self, task_json: str) -> str:
        """Invoked from JS to get task duration prediction from Python ML backend."""
        try:
            data = json.loads(task_json)
        except Exception:
            data = {}
        res = predict_task_time(data)
        return json.dumps(res)

    @Slot(str, str, result=str)
    def detectAnomalies(self, operator_id: str, session_json: str) -> str:
        """Invoked from JS to get digital twin anomalies from Python ML backend."""
        try:
            data = json.loads(session_json)
        except Exception:
            data = {}
        res = detect_anomalies(operator_id, data)
        return json.dumps(res)

    @Slot(str)
    def logIncident(self, incident_json: str):
        """Logs an operator incident to disk/console."""
        try:
            data = json.loads(incident_json)
            print(f"[CAT-INCIDENT-LOG] Incident recorded: {data}")
            self.incidentLogged.emit(incident_json)
        except Exception as e:
            print(f"[CAT-INCIDENT-LOG] Error logging incident: {e}")
