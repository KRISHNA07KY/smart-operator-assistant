"""backend/dummy_ml.py
Modular Dummy ML service for Caterpillar Smart Operator Assistant.
Pre-configured with realistic synthetic calculation logic matching the hackathon datasets,
ready to be swapped with trained models (scikit-learn / joblib / PyTorch) at any time.
"""
from typing import Dict, Any, List
import math


def predict_safety(inputs: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Predicts safety risk index (0-100), categorical risk level, and group factor contributions.
    
    Inputs can include:
        speed (km/h)
        distance (m, proximity to obstacles/workers)
        load (%)
        slope (degrees)
        visibility (%)
        seatbelt (bool or "Fastened"/"Unfastened")
    """
    speed = float(inputs.get("speed", 5.0))
    distance = float(inputs.get("distance", 8.0))
    load = float(inputs.get("load", 50.0))
    slope = float(inputs.get("slope", 5.0))
    visibility = float(inputs.get("visibility", 80.0))
    seatbelt = inputs.get("seatbelt", True)
    if isinstance(seatbelt, str):
        seatbelt = seatbelt.lower() in ("fastened", "true", "yes", "1")

    # Domain risk heuristic matching CAT excavator dynamics
    base_score = 12.0
    
    # Distance / Proximity contribution (inverse exponential)
    if distance < 2.0:
        prox_contrib = 45.0
    elif distance < 4.0:
        prox_contrib = 30.0
    elif distance < 7.0:
        prox_contrib = 15.0
    else:
        prox_contrib = 4.0

    # Speed contribution
    speed_contrib = (speed / 12.0) * 20.0

    # Slope contribution
    slope_contrib = (slope / 25.0) * 15.0

    # Load contribution
    load_contrib = (load / 100.0) * 10.0

    # Visibility penalty
    vis_penalty = max(0.0, (100.0 - visibility) / 100.0 * 15.0)

    # Seatbelt safety check
    seatbelt_penalty = 25.0 if not seatbelt else 0.0

    total_score = min(100.0, max(0.0, base_score + prox_contrib + speed_contrib + slope_contrib + load_contrib + vis_penalty + seatbelt_penalty))
    score = round(total_score, 1)

    if score >= 70.0:
        level = "CRITICAL" if score >= 85.0 else "HIGH"
    elif score >= 40.0:
        level = "MEDIUM"
    else:
        level = "LOW"

    # Shapley-style risk contributions
    contributions = [
        {"factor": "Proximity", "weight": round(prox_contrib, 1), "status": "Critical" if distance < 3 else "Normal"},
        {"factor": "Machine Speed", "weight": round(speed_contrib, 1), "status": "Elevated" if speed > 8 else "Normal"},
        {"factor": "Terrain Slope", "weight": round(slope_contrib, 1), "status": "Steep" if slope > 12 else "Normal"},
        {"factor": "Visibility", "weight": round(vis_penalty, 1), "status": "Low" if visibility < 60 else "Good"},
        {"factor": "Seatbelt", "weight": round(seatbelt_penalty, 1), "status": "Unfastened" if not seatbelt else "Fastened"},
    ]
    contributions.sort(key=lambda x: x["weight"], reverse=True)

    recommendation = "Maintain vigilance and standard safe operating distance."
    if level in ("HIGH", "CRITICAL"):
        if distance < 4.0:
            recommendation = "Personnel detected in blind zone! Immediately stop machine and verify visual contact."
        elif not seatbelt:
            recommendation = "Fasten seatbelt immediately before continuing machine operation."
        elif slope > 15.0:
            recommendation = "Steep terrain grade: Reduce machine speed and keep boom centered."
        else:
            recommendation = "Reduce travel speed and sound horn when manoeuvring."

    return {
        "score": score,
        "level": level,
        "contributions": contributions,
        "recommendation": recommendation,
        "model_version": "dummy-safety-v1.0"
    }


def predict_task_time(task: Dict[str, Any]) -> Dict[str, Any]:
    """Estimates remaining and total task duration with conformal 80% uncertainty bounds.
    
    Inputs can include:
        task_type, target_quantity, weather, operator_skill, machine_age, current_progress
    """
    baseline_minutes = float(task.get("estimated_duration", task.get("planned_time", 45.0)))
    progress = float(task.get("current_progress", 0.0))  # 0.0 to 1.0
    weather = str(task.get("weather", "Sunny")).lower()
    skill = str(task.get("skill", "Intermediate")).lower()
    machine_age = float(task.get("machine_age", 3.0))

    # Environmental factor
    weather_multiplier = 1.0
    if "rain" in weather:
        weather_multiplier = 1.18
    elif "mud" in weather or "fog" in weather or "dust" in weather:
        weather_multiplier = 1.12

    # Operator skill factor
    skill_multiplier = 1.0
    if "expert" in skill or "advanced" in skill:
        skill_multiplier = 0.90
    elif "beginner" in skill:
        skill_multiplier = 1.25

    # Machine aging degradation
    machine_multiplier = 1.0 + (machine_age * 0.02)

    total_pred = baseline_minutes * weather_multiplier * skill_multiplier * machine_multiplier
    rem_pred = max(2.0, total_pred * (1.0 - progress))

    # Conformal 80% coverage range (+- 15%)
    low_bound = round(rem_pred * 0.85, 1)
    high_bound = round(rem_pred * 1.18, 1)

    variance_pct = round(((total_pred - baseline_minutes) / baseline_minutes) * 100.0, 1)

    return {
        "predicted_total_min": round(total_pred, 1),
        "predicted_remaining_min": round(rem_pred, 1),
        "range_low_min": low_bound,
        "range_high_min": high_bound,
        "variance_pct": variance_pct,
        "confidence_score": 0.92,
        "factors": [
            {"factor": "Weather Condition", "impact_pct": round((weather_multiplier - 1.0) * 100, 1)},
            {"factor": "Operator Skill", "impact_pct": round((skill_multiplier - 1.0) * 100, 1)},
            {"factor": "Machine Age Degradation", "impact_pct": round((machine_multiplier - 1.0) * 100, 1)},
        ],
        "model_version": "dummy-tasktime-v1.0"
    }


def detect_anomalies(operator_id: str, session: Dict[str, Any]) -> Dict[str, Any]:
    """Personalized Operator Digital Twin anomaly detector.
    Computes personal z-score deviations against baseline.
    """
    idle_time_pct = float(session.get("idle_percentage", session.get("idle_time", 25.0)))
    fuel_rate = float(session.get("fuel_rate", 14.5))
    swing_harshness = float(session.get("swing_harshness", 1.2))

    # Baseline typical ranges for operator
    baselines = {
        "idle_percentage": {"mean": 18.0, "sd": 4.5, "unit": "%"},
        "fuel_rate": {"mean": 13.0, "sd": 1.8, "unit": "L/h"},
        "swing_harshness": {"mean": 1.0, "sd": 0.25, "unit": "g"},
    }

    idle_z = (idle_time_pct - baselines["idle_percentage"]["mean"]) / baselines["idle_percentage"]["sd"]
    fuel_z = (fuel_rate - baselines["fuel_rate"]["mean"]) / baselines["fuel_rate"]["sd"]
    swing_z = (swing_harshness - baselines["swing_harshness"]["mean"]) / baselines["swing_harshness"]["sd"]

    max_z = max(abs(idle_z), abs(fuel_z), abs(swing_z))
    is_anomaly = max_z > 2.0

    top_deviation = "Excessive Idle Time" if idle_z > 2.0 else "Elevated Fuel Burn" if fuel_z > 2.0 else "Aggressive Swing" if swing_z > 2.0 else "Normal"

    return {
        "operator_id": operator_id,
        "status": "UNUSUAL" if is_anomaly else "NORMAL",
        "anomaly_score": round(min(1.0, max_z / 3.5), 3),
        "top_deviation": top_deviation,
        "metrics": [
            {"metric": "Idle Time Ratio", "current": idle_time_pct, "baseline": "18.0%", "z": round(idle_z, 2)},
            {"metric": "Fuel Consumption Rate", "current": fuel_rate, "baseline": "13.0 L/h", "z": round(fuel_z, 2)},
            {"metric": "Hydraulic Swing Acceleration", "current": swing_harshness, "baseline": "1.0 g", "z": round(swing_z, 2)},
        ],
        "recommendation": "Recommend 5-min micro-learning on hydraulic power management." if is_anomaly else "Operating parameters match optimal efficiency baseline.",
        "model_version": "dummy-twin-v1.0"
    }
