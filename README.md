# SmartV2V — Software-Based Vehicle-to-Vehicle Communication and Collision Warning System

[![Platform: Software Defined Vehicle](https://img.shields.io/badge/Platform-Software%20Defined%20Vehicle%20(SDV)-blue.svg)]()
[![Type: Pure Software Simulation](https://img.shields.io/badge/Simulation-Zero%20Hardware%20Required-success.svg)]()
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)]()
[![React: 18](https://img.shields.io/badge/React-18.3-cyan.svg)]()
[![FastAPI: 0.110+](https://img.shields.io/badge/FastAPI-0.110%2B-emerald.svg)]()
[![Test Suite: 100% Pass](https://img.shields.io/badge/Tests-19%2F19%20Passing-brightgreen.svg)]()

> **SOFTWARE SIMULATION — NO PHYSICAL VEHICLES OR HARDWARE REQUIRED**  
> Designed for Software Defined Vehicle (SDV) academic capstones, automotive software engineering coursework, and intelligent vehicle research.

---

## 1. Project Overview

**SmartV2V** is a full-stack, software-only Vehicle-to-Vehicle (V2V) cooperative perception and forward collision avoidance warning simulator. It demonstrates how connected vehicles cooperatively exchange real-time state information (Basic Safety Messages) over wireless channels to anticipate and mitigate imminent road hazards long before they become visible to human drivers or onboard line-of-sight sensors.

### Key Highlights
- **100% Software-Based:** No microcontrollers (ESP32, Arduino), GPS chips, physical radio modules, or physical vehicles required.
- **Authoritative Backend Engine:** Python FastAPI engine managing physics integration, car-following kinetics, wireless packet loss, network latency queues, and safety evaluation at 20 Hz.
- **SAE J2735 & ETSI CAM Modeled:** Simulates periodic Basic Safety Message (BSM) broadcast within configurable Euclidean communication ranges.
- **Transparent Multi-Rule Safety Engine:** Time-to-Collision (TTC), Forward Collision Warning (FCW), Electronic Emergency Brake Light (EEBL), and 4-way Intersection Conflict Warning (ICW) with stateful debounce hysteresis.
- **Cockpit-Grade Dashboard:** Dark automotive aesthetic, local 2D road & intersection canvas with Retina rendering, live telemetry curves (Recharts), raw BSM packet inspector, wireless QoS analytics, and manual emergency brake actuators.

---

## 2. System Architecture

```mermaid
flowchart TD
    subgraph UI["Automotive Cockpit Dashboard (React + TypeScript + Tailwind)"]
        TopNav["Top Navigation & Status (WS Live / Running / Clock)"]
        Cards["Summary Telemetry Cards (Msg/s, Warnings, QoS)"]
        Canvas["Local 2D Road Canvas (Highway & Intersection View)"]
        Events["Live Safety Event Feed (Filterable by Severity)"]
        Charts["Telemetry Curves (Speed, Risk, Latency, Throughput)"]
        Drawer["Vehicle Inspector & Manual Emergency Brake Actuator"]
        Modals["BSM Packet Inspector & Network Analytics Modals"]
    end

    subgraph Backend["Authoritative SDV Backend Engine (FastAPI @ 20 Hz)"]
        FastAPIApp["FastAPI REST & WebSocket Gateway (/ws, /api)"]
        SimLoop["Authoritative Simulation Loop (Kinematics Integration dt=0.05s)"]
        
        subgraph CommBroker["V2V Wireless Communication Broker"]
            RangeFilter["Euclidean Range Filtering (dist <= R_comm)"]
            LossQueue["Simulated Packet Loss & Jitter Latency Queue"]
            Freshness["Per-Vehicle BSM Reception Table & Stale Detection"]
        end

        subgraph SafetyEngine["Rule-Based Collision Safety Engine"]
            TTC["Time-to-Collision Calculator (TTC = d_clear / v_closing)"]
            FCW["Forward Collision Warning & Safe Headway"]
            EEBL["Electronic Emergency Brake Light (EEBL) Broadcast"]
            ICW["4-Way Intersection Conflict Detector"]
            Debounce["Stateful Hysteresis Debouncer (Prevents Alert Flickering)"]
        end

        ScenarioMgr["Scenario Manager (Deterministic Repeatable Scenarios)"]
    end

    UI <===>|WebSocket 20 Hz Full State Stream| FastAPIApp
    UI <===>|REST Endpoints (Actuation / Settings / Logs)| FastAPIApp
    SimLoop --> CommBroker
    CommBroker --> SafetyEngine
    ScenarioMgr --> SimLoop
```

---

## 3. Technology Stack

### Frontend
- **Framework:** React 18 with Vite 6 & TypeScript
- **Styling:** Tailwind CSS (Dark automotive charcoal palette `#070A10`, `#0B0F19`, `#1E293B`, with cyan `#06B6D4` and blue `#3B82F6` accents)
- **Icons:** Lucide React
- **Data Visualization:** Recharts for real-time speed, throughput, collision risk, and latency curves
- **Visualization Canvas:** Native HTML5 Canvas with device-pixel-ratio scaling for responsive, high-framerate local 2D highway and intersection rendering (zero internet or map tiles required)

### Backend
- **Core Runtime:** Python 3.10+
- **Web Framework:** FastAPI with Starlette
- **Concurrency:** Python `asyncio` for non-blocking 20 Hz simulation ticks and streaming
- **Real-Time Transport:** WebSockets (`/ws`) for 20 Hz state streaming
- **Validation & Schemas:** Pydantic v2
- **State Store:** Authoritative in-memory state engine (zero external database required)

### Testing
- **Backend Test Suite:** Pytest + HTTPX TestClient (19 comprehensive unit tests)
- **Frontend Test Suite:** Vitest + React Testing Library

---

## 4. Project Folder Structure

```
open_elective/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py              # REST API endpoints & actuation handlers
│   │   │   └── websocket_manager.py   # WebSocket streaming hub
│   │   ├── core/
│   │   │   └── config.py              # Simulation constants, timings, and thresholds
│   │   ├── models/
│   │   │   ├── vehicle.py             # Vehicle telemetry, kinematics, & state models
│   │   │   ├── message.py             # SAE J2735 Basic Safety Message (BSM) schema
│   │   │   ├── event.py               # SafetyEvent models (EEBL, FCW, ICW)
│   │   │   └── metrics.py             # Wireless QoS & throughput metrics
│   │   └── services/
│   │       ├── simulation_engine.py   # Authoritative 20 Hz numerical physics loop
│   │       ├── v2v_broker.py          # Range filtering, packet loss, latency queue
│   │       ├── safety_engine.py       # TTC, FCW, EEBL, ICW & debouncer logic
│   │       └── scenario_manager.py    # 5 deterministic reproducible scenarios
│   ├── tests/
│   │   ├── conftest.py                # Test environment path setup
│   │   ├── test_physics.py            # Vehicle kinematics & acceleration tests
│   │   ├── test_v2v_broker.py         # Range cutoff, packet drop, stale tests
│   │   ├── test_safety_engine.py      # TTC formulas, debouncer, intersection tests
│   │   ├── test_scenarios.py          # Scenario reset & deterministic setup tests
│   │   └── test_api.py                # REST API and actuation endpoints tests
│   ├── requirements.txt
│   └── main.py                        # FastAPI entrypoint & background broadcaster
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TopNav.tsx             # Navigation, clock, scenario switcher, modals
│   │   │   ├── SummaryCards.tsx       # 6 telemetry cards with live calculations
│   │   │   ├── ScenarioBanner.tsx     # Scenario description & expected outcomes
│   │   │   ├── RoadCanvas.tsx         # 2D Canvas highway & intersection renderer
│   │   │   ├── LiveEventFeed.tsx      # Severity-filtered live safety event log
│   │   │   ├── TelemetryCharts.tsx    # Recharts live speed, risk, throughput curves
│   │   │   ├── VehicleInspector.tsx   # Telemetry drawer & manual emergency brake
│   │   │   ├── NetworkAnalyticsModal.tsx # Wireless QoS metrics & delay breakdown
│   │   │   ├── MessageInspectorModal.tsx # Raw BSM packet decode viewer
│   │   │   └── SimulationSettingsModal.tsx # Real-time slider controls
│   │   ├── services/
│   │   │   ├── api.ts                 # REST client
│   │   │   └── websocket.ts           # WebSocket subscriber with auto-reconnect
│   │   ├── types/
│   │   │   └── simulation.ts          # TypeScript interfaces matching backend models
│   │   ├── App.tsx                    # Main dashboard container
│   │   ├── main.tsx                   # React root entry
│   │   └── index.css                  # Tailwind styles and cockpit themes
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── tailwind.config.js
├── docs/
│   └── PROJECT_REPORT.md              # Formal academic SDV capstone report
└── README.md                          # Comprehensive setup & user manual
```

---

## 5. Local Setup and Installation

### Unified Single-Port Serving
The backend automatically detects the compiled frontend in `frontend/dist`. Running the backend on port `8000` serves the complete React dashboard, the REST API (`/api`), and WebSockets (`/ws`) from a single unified server.

See [`docs/DEPLOYMENT_GUIDE.md`](docs/DEPLOYMENT_GUIDE.md) for 1-click cloud deployment on Render, Railway, Docker, or instant public URL sharing for classroom presentations.

### Prerequisites
- Python 3.10+ installed
- Node.js 18+ and npm installed

### Backend Setup
1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the backend unit tests to verify the installation:
   ```bash
   python -m pytest tests -v
   ```
4. Start the FastAPI backend server:
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   *The backend will be live at `http://localhost:8000` with interactive Swagger docs at `http://localhost:8000/docs`.*

### Frontend Setup
1. Open a new terminal and navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your web browser and navigate to:
   ```
   http://localhost:5173
   ```

---

## 6. Pre-Defined Interactive Scenarios

SmartV2V includes 5 deterministic, reproducible automotive scenarios selectable directly from the dashboard:

| Scenario | Name | Category | Expected Automotive Outcome |
|---|---|---|---|
| **1** | **Normal Highway Traffic** | Baseline | Vehicles cruise at varying desired speeds (75–95 km/h) maintaining safe headway spacing. 0% loss, low latency. All nodes remain `SAFE`. |
| **2** | **Sudden Emergency Braking (EEBL)** | Safety Critical | Lead vehicle V2V-01 brakes hard ($-8.5\text{ m/s}^2$). Following vehicles receive immediate V2V EEBL packets, alerting drivers before visual line-of-sight reaction. |
| **3** | **Rear-End Collision Hazard (TTC)** | Kinematics | Slower vehicle V2V-01 (40 km/h) is approached by fast inattentive vehicle V2V-02 (115 km/h). Real-time TTC escalates from `SAFE` $\to$ `WARNING` ($<4.5\text{s}$) $\to$ `CRITICAL` ($<2.5\text{s}$). |
| **4** | **4-Way Intersection Conflict (ICW)** | Intersection | Perpendicular Eastbound and Northbound vehicles approach a blind crossing at $(300\text{m}, 50\text{m})$ simultaneously without traffic lights. Conflicting arrival delta $|\Delta T| < 1.2\text{s}$ triggers `CRITICAL` alert. |
| **5** | **Communication Failure** | Cyber-Physical | 65% packet loss and 350ms latency introduced. Demonstrates delayed alerts and stale telemetry counters under degraded RF channel conditions. |

---

## 7. Mathematical Formulations & Safety Engine

### 1. Kinematics (Authoritative 20 Hz Update Loop)
$$\Delta t = 0.05 \text{ seconds}$$
$$v(t + \Delta t) = \max\left(0.0, v(t) + a(t) \cdot \Delta t \cdot \mu_{\text{speed}}\right)$$
$$\Delta x = v(t + \Delta t) \cdot \cos(\theta) \cdot \Delta t \cdot \mu_{\text{speed}}$$
$$\Delta y = v(t + \Delta t) \cdot \sin(\theta) \cdot \Delta t \cdot \mu_{\text{speed}}$$

### 2. Time-to-Collision (TTC)
For vehicles $A$ (follower) and $B$ (leader) in the same lane:
$$d_{\text{clear}} = x_B - x_A - L_{\text{vehicle}}$$
$$v_{\text{closing}} = v_A - v_B$$
$$\text{TTC} = \frac{d_{\text{clear}}}{v_{\text{closing}}} \quad (\text{evaluated when } v_{\text{closing}} > 0.1\text{ m/s})$$

### 3. Electronic Emergency Brake Light (EEBL)
Triggered whenever $a_i \le -4.5\text{ m/s}^2$ or manual emergency brake is triggered. Transmitted via V2V Basic Safety Message to all neighbors within Euclidean range $d \le R_{\text{comm}}$.

### 4. Stateful Hysteresis Debouncing
Eliminates high-frequency flickering of warnings:
- Escalation to higher alert requires **2 consecutive cycles**.
- De-escalation to lower alert requires **3 consecutive safe cycles**.

---

## 8. REST & WebSocket API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & platform metadata |
| `GET` | `/api/simulation/status` | Complete authoritative state snapshot |
| `GET` | `/api/vehicles` | List of all simulated vehicles |
| `GET` | `/api/vehicles/{id}` | Telemetry for a specific vehicle |
| `GET` | `/api/vehicles/{id}/messages` | Per-vehicle received message table (BSM) |
| `GET` | `/api/events` | Recent safety events log |
| `GET` | `/api/metrics` | Wireless QoS and throughput statistics |
| `GET` | `/api/scenarios` | Predefined scenario definitions |
| `GET` | `/api/messages/logs` | Raw packet transmission history |
| `POST` | `/api/simulation/start` | Start authoritative simulation loop |
| `POST` | `/api/simulation/pause` | Pause simulation |
| `POST` | `/api/simulation/resume` | Resume simulation |
| `POST` | `/api/simulation/stop` | Stop simulation |
| `POST` | `/api/simulation/reset` | Reset simulation time and vehicle states |
| `POST` | `/api/simulation/scenario` | Switch active scenario (`{"scenario_id": "..."}`) |
| `POST` | `/api/simulation/settings` | Update speed, range, latency, or packet loss |
| `POST` | `/api/vehicles/{id}/emergency-brake` | Actuate physical emergency brake on vehicle |
| `WS` | `/ws` | Real-time 20 Hz bidirectional WebSocket stream |

---

## 9. Running Tests

### Backend Unit Tests
```bash
python -m pytest backend/tests -v
```
Output:
```
============================= test session starts =============================
19 passed in 0.95s
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 10. Limitations & Future Enhancements
- **Current Limitation:** Planar 2D coordinate system. Future work can extend this to 3D elevation maps with GPS coordinate translation (WGS84).
- **Channel Modeling:** Current wireless broker utilizes probabilistic packet drop and Gaussian latency. Future revisions could integrate ray-tracing RF obstruction around buildings.
- **Lateral Evasion:** Future iterations could add autonomous steering lane-change maneuvers in response to EEBL warnings.
