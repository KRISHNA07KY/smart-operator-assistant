"""
Dummy Task Data & Storage
Populated directly from Image 1 dataset.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TaskItem:
    task_id: str
    task_type: str
    weather: str
    operator_skill: str
    machine_age: int  # in years
    estimated_time: int  # in minutes
    actual_time: Optional[int]  # in minutes (None if still in progress)
    status: str  # "Completed", "In Progress", "Pending"
    elapsed_time: int = 0  # current tracked minutes if In Progress

def get_initial_tasks() -> List[TaskItem]:
    """
    Returns the initial tasks matching Image 1:
    T001 | Earth Excavation | Sunny  | Expert       | 2 | 60 | 55
    T002 | Trenching        | Rainy  | Intermediate | 4 | 45 | 52
    T003 | Material Loading | Cloudy | Beginner     | 3 | 30 | 42
    T004 | Grading          | Sunny  | Expert       | 5 | 35 | 33
    T005 | Demolition       | Windy  | Intermediate | 6 | 90 | 105
    """
    return [
        TaskItem(
            task_id="T001",
            task_type="Earth Excavation",
            weather="Sunny",
            operator_skill="Expert",
            machine_age=2,
            estimated_time=60,
            actual_time=55,
            status="Completed",
            elapsed_time=55
        ),
        TaskItem(
            task_id="T002",
            task_type="Trenching",
            weather="Rainy",
            operator_skill="Intermediate",
            machine_age=4,
            estimated_time=45,
            actual_time=None,
            status="In Progress",
            elapsed_time=28
        ),
        TaskItem(
            task_id="T003",
            task_type="Material Loading",
            weather="Cloudy",
            operator_skill="Beginner",
            machine_age=3,
            estimated_time=30,
            actual_time=None,
            status="Pending",
            elapsed_time=0
        ),
        TaskItem(
            task_id="T004",
            task_type="Grading",
            weather="Sunny",
            operator_skill="Expert",
            machine_age=5,
            estimated_time=35,
            actual_time=None,
            status="Pending",
            elapsed_time=0
        ),
        TaskItem(
            task_id="T005",
            task_type="Demolition",
            weather="Windy",
            operator_skill="Intermediate",
            machine_age=6,
            estimated_time=90,
            actual_time=None,
            status="Pending",
            elapsed_time=0
        ),
    ]
