"""
Dummy Machine Learning Predictor Hook for Task Time Estimation
This module defines the structured data contract between the frontend UI
and the Machine Learning model. When you are ready to train and deploy your
real scikit-learn / XGBoost model, simply replace the prediction logic inside
`predict_task_time()`.
"""

from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class TaskTimeInput:
    task_type: str        # e.g., "Earth Excavation", "Trenching", "Material Loading", "Grading", "Demolition"
    weather: str          # e.g., "Sunny", "Rainy", "Cloudy", "Windy", "Stormy"
    operator_skill: str   # e.g., "Beginner", "Intermediate", "Expert"
    machine_age: int      # in years (1 to 10)

@dataclass
class FactorImpact:
    factor_name: str
    impact_pct: float     # e.g. +15.0 or -8.0
    description: str

@dataclass
class MLPredictionResult:
    predicted_minutes: int
    baseline_minutes: int
    variance_minutes: int
    variance_pct: float
    confidence_score: int  # 0 to 100%
    factor_impacts: List[FactorImpact] = field(default_factory=list)
    ai_recommendations: List[str] = field(default_factory=list)
    is_delayed: bool = False

def predict_task_time(task_input: TaskTimeInput) -> MLPredictionResult:
    """
    Hook function for ML task duration prediction.
    Currently uses an empirical baseline derived from Image 1 training data.
    
    Replace this implementation with:
        model = joblib.load('cat_time_predictor.pkl')
        return model.predict(features)
    """
    # 1. Base duration by task type (derived from standard CAT operation specs)
    base_times = {
        "Earth Excavation": 60,
        "Trenching": 45,
        "Material Loading": 30,
        "Grading": 35,
        "Demolition": 90
    }
    baseline = base_times.get(task_input.task_type, 50)
    
    # 2. Weather impact multiplier
    weather_multipliers = {
        "Sunny": 0.0,
        "Cloudy": 0.05,
        "Windy": 0.16,
        "Rainy": 0.18,
        "Stormy": 0.35
    }
    weather_delta_pct = weather_multipliers.get(task_input.weather, 0.05)
    
    # 3. Operator skill factor
    skill_multipliers = {
        "Expert": -0.08,        # ~8% faster
        "Intermediate": 0.12,   # ~12% slower than baseline ideal
        "Beginner": 0.38        # ~38% slower (as seen in Image 1 T003: 30m -> 42m)
    }
    skill_delta_pct = skill_multipliers.get(task_input.operator_skill, 0.10)
    
    # 4. Machine age impact (hydraulic wear & cycle delay)
    # Machine age adds ~1.8% delay per year over 2 years
    age_delta_pct = max(0.0, (task_input.machine_age - 2) * 0.025)
    
    # Calculate total predicted duration
    total_multiplier = 1.0 + weather_delta_pct + skill_delta_pct + age_delta_pct
    predicted = int(round(baseline * total_multiplier))
    
    variance = predicted - baseline
    variance_pct = round((variance / baseline) * 100, 1)
    
    # Build factor impact breakdown
    factor_impacts = [
        FactorImpact(
            factor_name=f"Weather ({task_input.weather})",
            impact_pct=round(weather_delta_pct * 100, 1),
            description="Wet/windy soil reduces traction and boom swing precision." if weather_delta_pct > 0.1 else "Nominal environmental condition."
        ),
        FactorImpact(
            factor_name=f"Operator Skill ({task_input.operator_skill})",
            impact_pct=round(skill_delta_pct * 100, 1),
            description="Skill curve affects load cycle fluidity and trench wall grading."
        ),
        FactorImpact(
            factor_name=f"Machine Age ({task_input.machine_age} yrs)",
            impact_pct=round(age_delta_pct * 100, 1),
            description="Hydraulic pressure latency and swing drive response delay." if age_delta_pct > 0 else "Peak optimal mechanical condition."
        )
    ]
    
    # Confidence score (simulated model certainty)
    confidence = 92 if task_input.task_type in base_times else 78
    if task_input.weather in ["Rainy", "Stormy"]:
        confidence -= 4
        
    # In-cab AI recommendations
    ai_recs = []
    if task_input.weather in ["Rainy", "Stormy"]:
        ai_recs.append("Wet Ground Warning: Activate Heavy Lift / Eco-Traction mode to prevent undercarriage slip.")
    if task_input.operator_skill == "Beginner":
        ai_recs.append("Grade Assist: Turn on CAT Grade 2D assist to automatically maintain target slope.")
    if task_input.machine_age >= 5:
        ai_recs.append("Hydraulic Pre-check: Ensure hydraulic fluid reaches 50°C before heavy digging cycles.")
    if not ai_recs:
        ai_recs.append("Optimal Work Conditions: High efficiency expected. Maintain standard bucket payload.")
        
    return MLPredictionResult(
        predicted_minutes=predicted,
        baseline_minutes=baseline,
        variance_minutes=variance,
        variance_pct=variance_pct,
        confidence_score=confidence,
        factor_impacts=factor_impacts,
        ai_recommendations=ai_recs,
        is_delayed=(variance > 0)
    )
