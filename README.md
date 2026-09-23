# CAT Smart Operator Assistant-In-Cab Intelligent Dashboard

> **Predict → Explain → Simulate → Learn**  
> An intelligent in-cab companion application for Caterpillar excavators and heavy machinery. Built with **Python PySide6 (Qt)**, featuring hardware-accelerated **3D Three.js simulation**, a **4-language multi-lingual engine**, and a modular **Python ML backend**.

---

## Key Features

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

## Technology Stack & Frameworks

| Layer | Technologies & Frameworks |
|---|---|
| **Frontend** | React 18, JavaScript (ES6+), HTML5, CSS3, Tailwind CSS, Vite, interactive in-cab dashboards, data visualisation (Recharts, Framer Motion), 3D web visualisation (Three.js, React Three Fiber `@react-three/fiber`, `@react-three/drei`), Lucide icons. |
| **Desktop Shell** | Python PySide6 (Qt 6), `QWebEngineView` (hardware-accelerated WebGL engine), `QWebChannel` (bi-directional IPC bridge), PyInstaller (standalone Windows `.exe` packaging). |
| **Backend** | Python, FastAPI architecture, REST APIs, local multi-threaded HTTP server (`backend/app.py`), PySide6 Qt Bridge (`backend/bridge.py`). |
| **AI/ML** | Python, Pandas, NumPy, Scikit-learn, tree-based ML models and anomaly detection (with modular model-serving interfaces in `backend/dummy_ml.py`). |
| **Data** | Process-driven synthetic mining dataset with machine health, environmental conditions, operator behaviour, haul cycles, productivity and safety-event data. |
| **Database/Storage** | PostgreSQL / structured data storage. |
| **Simulation** | Interactive 3D operational scenarios (rigged CAT EXC-204 excavator, moving worker kinematics, dynamic blind-zone threat radar, dual Site/Cab views) and What-If counterfactual parameter simulation. |
| **AI Assistant** | AI/LLM-based natural-language interaction connected to the system's predictions and recommendations, featuring a complete **4-language multi-lingual engine** (English, தமிழ் / Tamil, हिन्दी / Hindi, తెలుగు / Telugu). |

---

## Quick Start

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

## Project Architecture

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

## License
Internal Hackathon Project • Caterpillar Inc.
