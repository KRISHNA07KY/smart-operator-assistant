"""
Incident & Working Conditions Logging Model
Allows operators to log safety hazards, near-misses, and harsh working conditions.
"""

from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class IncidentReport:
    incident_id: str
    timestamp: str
    category: str              # e.g., "Near Miss", "Pedestrian in Blindspot", "Trench Wall Slump", "Equipment Fault"
    severity: str              # "Low", "Medium", "High", "Critical"
    working_conditions: str    # e.g., "Heavy Rain, Poor Visibility, Muddy Slope"
    location: str
    description: str
    reported_by: str           # "OP1001"
    status: str                # "Logged", "Under Review", "Resolved"

def get_initial_incidents() -> List[IncidentReport]:
    return [
        IncidentReport(
            incident_id="INC-2025-001",
            timestamp="2025-05-01 10:05:12",
            category="Seatbelt Non-Compliance Alert",
            severity="Medium",
            working_conditions="Rainy, High Humidity, Slippery Cab Steps",
            location="Zone B - Trenching Trench #4",
            description="Operator unfastened seatbelt while machine was active to inspect rear hydraulic line.",
            reported_by="OP1001",
            status="Under Review"
        ),
        IncidentReport(
            incident_id="INC-2025-002",
            timestamp="2025-05-01 14:22:45",
            category="Pedestrian in Swing Radius",
            severity="High",
            working_conditions="Sunny, High Dust, High Ambient Noise",
            location="Zone A - Bulk Excavation Pit",
            description="Grade checker walked within 4m of boom swing radius without radio announcement. Proximity radar alarmed.",
            reported_by="OP1001",
            status="Logged"
        ),
        IncidentReport(
            incident_id="INC-2025-003",
            timestamp="2025-05-02 09:15:30",
            category="Excessive Idling / Staged Wait",
            severity="Low",
            working_conditions="Rainy, Waterlogged Soil",
            location="Staging Area East",
            description="Haul truck delay caused 60-minute machine idle in queue.",
            reported_by="OP1001",
            status="Resolved"
        )
    ]
