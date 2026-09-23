# CAT Smart Operator Assistant — In-Cab Intelligent Dashboard

> **Predict → Explain → Simulate → Learn**  
> An intelligent in-cab companion application for Caterpillar excavators and heavy machinery. Built with **Python PySide6 (Qt)**, featuring hardware-accelerated **3D Three.js simulation**, a **4-language multi-lingual engine**, and a modular **Python ML backend**.

---

## 🌟 Key Features

- **10 Complete In-Cab Screens**:
  1. **Overview**: Real-time shift timeline, active task progress, 80% confidence range, top-down radar, risk gauge, and digital twin status.
  2. **Live Machine**: Cockpit telemetry gauges (RPM, hydraulic pressure, fuel consumption, inclinometers).
  3. **Daily Tasks**: Daily schedule (T001–T005), active countdown, and task completion estimator.
  4. **Safety Center**: Seatbelt compliance monitor, 360° proximity radar with danger envelopes, incident history logger.
  5. **Operator Twin**: Personal baseline comparisons and Isolation Forest anomaly alerts.
  6. **Training Hub**: Interactive microlearning drills (Blind-Zone Awareness, Idling Reduction, Slope Operations).
  7. **3D Simulator**: Interactive Three.js 3D excavator, animated ground worker entering blind zone, site props, cab/site camera toggles, and decision analysis.
  8. **Safety Replay**: Timeline replay of historical safety incidents.
  9. **What-If Analysis**: Real-time counterfactual slider analysis (Speed, Slope, Load, Visibility).
  10. **Analytics**: Fleet risk distribution, idle time ratio trends, and fuel efficiency metrics.

- **3D Hardware-Accelerated Simulation**:
  - Articulated CAT EXC-204 excavator with rotating boom and tracks.
  - Animated worker entering the rear-left blind zone.
  - Interactive decision pauses (Options A, B, C, D) and decision impact analysis.
  - Dual camera views (**Site View** ↔ **Cab View**).

- **Multi-Lingual Support (4 Languages)**:
  - English (`en`), தமிழ் (Tamil - `ta`), हिन्दी (Hindi - `hi`), and తెలుగు (Telugu - `te`) with persistent storage.

- **Dual-Mode Desktop Shell**:
  - Switch between **3D Assistant (Full Experience)** and **In-Cab Widgets (Classic Qt)** with one click.
  - Fullscreen support (`F11`) and hot reload (`Ctrl+R`).

- **Modular Python ML Backend**:
  - Pre-configured with dummy ML services for Safety Risk scoring, Task Time estimation, and Operator Digital Twin anomaly detection.
  - Easily swappable with real scikit-learn / joblib / PyTorch models in `backend/dummy_ml.py`.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PySide6

### Running the Python Application
```bash
py main.py
```

### Running the Pre-compiled Executable
Run `dist/CatOperatorAssistant.exe` directly on Windows without needing Python or Node.js.

### Running Test Suite
```bash
py -m unittest tests/test_full_suite.py
py tests/smoke_test.py
```

---

## 📁 Project Architecture

```
.
├── backend/                  # Python backend & ML services
│   ├── app.py                # Local HTTP server & API endpoints
│   ├── dummy_ml.py           # Modular ML prediction hooks (Safety, Task Time, Twin)
│   └── bridge.py             # QtWebChannel bi-directional bridge
├── frontend/                 # High-fidelity React + Three.js UI
│   ├── dist/                 # Production pre-bundled assets (committed for standalone run)
│   └── src/                  # 10 screens, 3D canvas, i18n dictionaries
├── widgets/                  # Native PySide6 in-cab widgets (Classic view)
├── utils/                    # Vector icon manager & SVG renderers
├── models/                   # Machine learning models & metadata
├── tests/                    # Unit tests & smoke tests
├── config.py                 # Industrial Caterpillar theme & styling
└── main.py                   # PySide6 application entry point
```

---

## 📄 License
Internal Hackathon Project • Caterpillar Inc.
