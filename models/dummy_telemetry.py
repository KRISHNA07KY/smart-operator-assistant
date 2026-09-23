"""
Dummy Telemetry & Machine Usage Model
Populated directly from Image 2 telemetry dataset, with rule-based anomaly detection.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class TelemetryRecord:
    timestamp: str
    machine_id: str
    operator_id: str
    engine_hours: float
    fuel_used_l: float
    load_cycles: int
    idling_time_min: int
    seatbelt_status: str       # "Fastened" or "Unfastened"
    safety_alert_triggered: str # "Yes" or "No"

@dataclass
class AnomalyAlert:
    alert_id: str
    severity: str              # "CRITICAL", "WARNING", "INFO"
    title: str
    description: str
    timestamp: str
    metric_value: str
    recommendation: str

def get_initial_telemetry() -> List[TelemetryRecord]:
    """
    Returns initial historical telemetry from Image 2:
    Timestamp           | Machine ID | Operator ID | Engine Hours | Fuel Used (L) | Load Cycles | Idling Time (min) | Seatbelt Status | Safety Alert Triggered
    2025-05-01 08:00:00 | EXC001     | OP1001      | 1523.5       | 5.2           | 12          | 30                | Fastened        | No
    2025-05-01 10:00:00 | EXC001     | OP1001      | 1524.8       | 3.8           | 2           | 55                | Unfastened      | Yes
    2025-05-01 14:00:00 | EXC001     | OP1001      | 1526.5       | 6.1           | 10          | 15                | Fastened        | No
    2025-05-02 09:00:00 | EXC001     | OP1001      | 1530.2       | 2.0           | 1           | 60                | Unfastened      | Yes
    """
    return [
        TelemetryRecord(
            timestamp="2025-05-01 08:00:00",
            machine_id="EXC001",
            operator_id="OP1001",
            engine_hours=1523.5,
            fuel_used_l=5.2,
            load_cycles=12,
            idling_time_min=30,
            seatbelt_status="Fastened",
            safety_alert_triggered="No"
        ),
        TelemetryRecord(
            timestamp="2025-05-01 10:00:00",
            machine_id="EXC001",
            operator_id="OP1001",
            engine_hours=1524.8,
            fuel_used_l=3.8,
            load_cycles=2,
            idling_time_min=55,
            seatbelt_status="Unfastened",
            safety_alert_triggered="Yes"
        ),
        TelemetryRecord(
            timestamp="2025-05-01 14:00:00",
            machine_id="EXC001",
            operator_id="OP1001",
            engine_hours=1526.5,
            fuel_used_l=6.1,
            load_cycles=10,
            idling_time_min=15,
            seatbelt_status="Fastened",
            safety_alert_triggered="No"
        ),
        TelemetryRecord(
            timestamp="2025-05-02 09:00:00",
            machine_id="EXC001",
            operator_id="OP1001",
            engine_hours=1530.2,
            fuel_used_l=2.0,
            load_cycles=1,
            idling_time_min=60,
            seatbelt_status="Unfastened",
            safety_alert_triggered="Yes"
        ),
    ]

def evaluate_anomalies(records: List[TelemetryRecord]) -> List[AnomalyAlert]:
    """
    Analyzes telemetry records for unusual behavior:
    1. Excessive Idling (>45 minutes threshold)
    2. Unsafe Operation (Unfastened seatbelt with engine running)
    3. Low Operational Efficiency (High idling & fuel burn with <=2 load cycles)
    """
    anomalies = []
    
    for idx, rec in enumerate(records):
        # 1. Excessive idling
        if rec.idling_time_min >= 45:
            anomalies.append(
                AnomalyAlert(
                    alert_id=f"IDLE-{idx+1:03d}",
                    severity="WARNING",
                    title="Excessive Machine Idling Detected",
                    description=f"Idling time reached {rec.idling_time_min} mins (Threshold: 45m). Wasting fuel and increasing carbon footprint.",
                    timestamp=rec.timestamp,
                    metric_value=f"{rec.idling_time_min} min idle",
                    recommendation="Enable CAT Auto Engine Idle Shutdown (AES) or shut down engine during haul truck delays."
                )
            )
            
        # 2. Unfastened Seatbelt during active engine session
        if rec.seatbelt_status.lower() == "unfastened":
            anomalies.append(
                AnomalyAlert(
                    alert_id=f"SAFE-{idx+1:03d}",
                    severity="CRITICAL",
                    title="Unsafe Operation: Seatbelt Unfastened",
                    description="Engine was operating while operator seatbelt latch sensor detected unfastened condition.",
                    timestamp=rec.timestamp,
                    metric_value="Seatbelt Unfastened",
                    recommendation="Immediate cab audio warning triggered. Compliance logged to fleet safety supervisor."
                )
            )
            
        # 3. Low Productivity / Inefficiency
        if rec.idling_time_min > 30 and rec.load_cycles <= 2:
            anomalies.append(
                AnomalyAlert(
                    alert_id=f"EFF-{idx+1:03d}",
                    severity="INFO",
                    title="Abnormal Duty Cycle Discrepancy",
                    description=f"Only {rec.load_cycles} load cycles completed despite {rec.fuel_used_l}L fuel consumption.",
                    timestamp=rec.timestamp,
                    metric_value=f"{rec.load_cycles} cycles / {rec.fuel_used_l}L",
                    recommendation="Inspect job site staging bottlenecks or check for unauthorized machine run."
                )
            )
            
    return anomalies
