# SmartV2V: Software-Based Vehicle-to-Vehicle Communication and Collision Warning Platform
## College Capstone / SDV (Software Defined Vehicle) Project Technical Report

**Project Title:** SmartV2V: Software-Defined Vehicle-to-Vehicle Communication and Forward Collision Avoidance Warning System  
**Domain:** Automotive Software Engineering, Software Defined Vehicles (SDV), Intelligent Transportation Systems (ITS)  
**Author / Team:** SDV Open Elective Research Team  
**Date:** Academic Year 2026  
**Status:** Software Simulation — No Physical Vehicles Connected  

---

## 1. Abstract

Connected and Autonomous Vehicles (CAVs) and modern Software Defined Vehicles (SDVs) require cooperative perception mechanisms to overcome the physical limitations of onboard line-of-sight sensors (such as radar, lidar, and optical cameras). Vehicle-to-Vehicle (V2V) communication enables vehicles to cooperatively broadcast kinematic state and safety intent over wireless links, alerting surrounding vehicles to imminent road hazards before they become visually perceptible.

This report presents **SmartV2V**, a comprehensive, software-only V2V simulation and collision warning platform built from first principles. Running purely on local consumer hardware without requiring physical microcontrollers (e.g., ESP32, Arduino) or external radio transceivers, SmartV2V models authoritative vehicle kinematics, multi-lane and 4-way intersection scenarios, wireless channel characteristics (Euclidean range filtering, RF packet loss, and queue latency), and a rule-based safety engine incorporating Time-to-Collision (TTC), Forward Collision Warning (FCW), Electronic Emergency Brake Light (EEBL), and Intersection Conflict Warning (ICW) with stateful hysteresis debouncing. The platform features an automotive-grade dark cockpit dashboard displaying real-time 2D road visualizations, live telemetry curves, a packet inspector, and actuation controls.

---

## 2. Problem Statement and Motivation

Traditional Advanced Driver Assistance Systems (ADAS) rely on ego-vehicle onboard sensors. These sensors suffer from fundamental physical constraints:
1. **Blind Spots and Occlusion:** A large lead vehicle (e.g., a commercial truck) blocks the line of sight to a decelerating vehicle ahead.
2. **Adverse Weather:** Rain, dense fog, and nighttime glare degrade optical and lidar performance.
3. **Latency of Driver Reaction:** By the time a driver perceives mechanical brake lights, human reaction delay (average 1.0–1.5 seconds) severely diminishes available stopping clearance.

While standardized cooperative protocols like SAE J2735 and ETSI Cooperative Awareness Messages (CAM) address these limitations, academic institutions and automotive software students frequently lack expensive DSRC / C-V2X radio hardware rigs or physical test vehicles. There exists a crucial need for a high-fidelity, deterministic software simulator that faithfully demonstrates SDV principles, cooperative message exchange, network degradation effects, and safety algorithms in a self-contained local environment.

---

## 3. Mathematical Foundations and System Modeling

### 3.1 Kinematics Integration
Each vehicle $i$ is modeled with continuous longitudinal position $x_i$, lateral position $y_i$, forward velocity $v_i$, longitudinal acceleration $a_i$, and heading angle $\theta_i$. At authoritative simulation timestep $\Delta t = 0.05\text{ s}$ (20 Hz loop):

$$v_i(t + \Delta t) = \max\left(0, v_i(t) + a_i(t) \cdot \Delta t \cdot \mu_{\text{speed}}\right)$$

$$x_i(t + \Delta t) = x_i(t) + v_i(t + \Delta t) \cdot \cos\left(\frac{\pi \theta_i}{180}\right) \cdot \Delta t \cdot \mu_{\text{speed}}$$

$$y_i(t + \Delta t) = y_i(t) + v_i(t + \Delta t) \cdot \sin\left(\frac{\pi \theta_i}{180}\right) \cdot \Delta t \cdot \mu_{\text{speed}}$$

where $\mu_{\text{speed}}$ is the user-configured simulation speed multiplier.

### 3.2 Time-to-Collision (TTC) Formulation
For vehicle $A$ (follower) approaching vehicle $B$ (leader) in the identical lane ($\text{lane}_A = \text{lane}_B, x_B > x_A$):

The net longitudinal clearance $d_{\text{clear}}$ accounting for vehicle physical length $L = 4.8\text{ m}$ is:
$$d_{\text{clear}} = x_B - x_A - L$$

The relative closing velocity $v_{\text{closing}}$ is:
$$v_{\text{closing}} = v_A - v_B$$

When $v_{\text{closing}} > 0.1\text{ m/s}$ and $d_{\text{clear}} > 0$, the projected Time-to-Collision is calculated as:
$$\text{TTC} = \frac{d_{\text{clear}}}{v_{\text{closing}}}$$

If $v_{\text{closing}} \le 0$, the vehicles are diverging or maintaining constant relative separation; thus, no forward collision is geometrically imminent.

#### ISO 15623 / SAE J2735 Safety Thresholds:
$$\text{Risk Level} = \begin{cases} 
\text{CRITICAL}, & \text{if } 0 < \text{TTC} \le 2.5\text{ s} \text{ or EEBL active} \\
\text{WARNING}, & \text{if } 2.5\text{ s} < \text{TTC} \le 4.5\text{ s} \text{ or } d_{\text{clear}} < d_{\text{safe}} \\
\text{SAFE}, & \text{otherwise}
\end{cases}$$

### 3.3 Intersection Conflict Warning (ICW) Formulation
At a perpendicular crossing centered at $(x_{\text{int}}, y_{\text{int}})$ with conflict zone radius $R_{\text{conf}} = 18.0\text{ m}$:
For an Eastbound vehicle $E$ arriving along $y = y_{\text{int}}$ and a Northbound vehicle $N$ arriving along $x = x_{\text{int}}$:

$$T_{\text{enter}}^E = \frac{(x_{\text{int}} - x_E) - R_{\text{conf}}}{v_E}, \quad T_{\text{exit}}^E = \frac{(x_{\text{int}} - x_E) + R_{\text{conf}}}{v_E}$$

$$T_{\text{enter}}^N = \frac{(y_{\text{int}} - y_N) - R_{\text{conf}}}{v_N}, \quad T_{\text{exit}}^N = \frac{(y_{\text{int}} - y_N) + R_{\text{conf}}}{v_N}$$

Conflict occurs when entry/exit intervals overlap:
$$\max(T_{\text{enter}}^E, T_{\text{enter}}^N) \le \min(T_{\text{exit}}^E, T_{\text{exit}}^N)$$
with arrival delta $|\Delta T| = |T_{\text{enter}}^E - T_{\text{enter}}^N| < 1.2\text{ s}$ triggering a `CRITICAL` intersection conflict warning.

### 3.4 Stateful Hysteresis Debouncing
To prevent high-frequency warning alert flickering near boundary conditions:
- **Escalation** (SAFE $\to$ WARNING or WARNING $\to$ CRITICAL) requires $N_{\text{escalate}} = 2$ consecutive evaluation ticks.
- **De-escalation** (CRITICAL $\to$ WARNING or WARNING $\to$ SAFE) requires $N_{\text{deescalate}} = 3$ consecutive safe evaluation ticks.

---

## 4. Software Architecture and Design Patterns

SmartV2V adheres strictly to the **Software Defined Vehicle (SDV)** architectural paradigm: separation of concerns between Authoritative Physics, Cyber-Physical Communication Broker, Safety Engine, REST/WebSocket Gateway, and Real-Time Cockpit Presentation.

```
+-----------------------------------------------------------------+
|                       Vite React Client                         |
|  +----------------+  +--------------------+  +---------------+  |
|  | RoadCanvas 2D  |  | Summary Telemetry  |  | Live Event    |  |
|  | HTML5 Canvas   |  | Recharts Curves    |  | Feed Drawer   |  |
|  +----------------+  +--------------------+  +---------------+  |
+-----------------------------------------------------------------+
                                ^
                     WebSocket (20 Hz) / REST API
                                v
+-----------------------------------------------------------------+
|                    FastAPI Backend Engine                       |
|                                                                 |
|   +---------------------------------------------------------+   |
|   | Simulation Engine (Authoritative Physics Loop @ 20 Hz)  |   |
|   +---------------------------------------------------------+   |
|              |                                    |             |
|              v                                    v             |
|   +-----------------------+            +--------------------+   |
|   | V2V Comm Broker       |            | Safety Engine      |   |
|   | - Range Filter        |            | - TTC Calculator   |   |
|   | - Queue Delay         |----------->| - FCW Predictor    |   |
|   | - Packet Loss         | (BSM rx)   | - EEBL Warning     |   |
|   | - Freshness Stale     |            | - ICW Conflict     |   |
|   +-----------------------+            +--------------------+   |
+-----------------------------------------------------------------+
```

---

## 5. Pre-Defined Demonstration Scenarios

1. **Scenario 1: Normal Highway Flow (Baseline)**
   - Smooth multi-lane cruising with Intelligent Driver Model (IDM) car-following headway.
   - Outcome: All nodes remain `SAFE`; wireless packet delivery is 100%.

2. **Scenario 2: Sudden Emergency Braking (EEBL)**
   - Lead vehicle V2V-01 detects an obstacle and decelerates at $-8.5\text{ m/s}^2$.
   - Outcome: V2V Basic Safety Message broadcasts `EMERGENCY_BRAKE_ACTIVE` flag immediately. Following vehicle V2V-02 detects risk and issues a `CRITICAL` alert prior to visual line-of-sight perception.

3. **Scenario 3: Rear-End Collision Hazard (TTC Escalation)**
   - Fast follower V2V-02 (115 km/h) approaches slow leader V2V-01 (40 km/h) in the same lane.
   - Outcome: Demonstrates smooth, testable escalation of calculated TTC from `SAFE` ($>4.5\text{s}$) $\to$ `WARNING` ($<4.5\text{s}$) $\to$ `CRITICAL` ($<2.5\text{s}$).

4. **Scenario 4: 4-Way Intersection Conflict (ICW)**
   - Perpendicular paths arriving at a blind intersection $(300\text{m}, 50\text{m})$ simultaneously.
   - Outcome: Projected time to conflict zone overlaps within 1.2s; `CRITICAL` Intersection Conflict Warning triggered for both vehicles.

5. **Scenario 5: Degraded Communication & Packet Loss**
   - High RF packet loss (65%) and high latency (350ms) introduced.
   - Outcome: Demonstrates degraded delivery ratio, stale message counters, and delayed safety warning alerts due to dropped packets.

---

## 6. Verification and Test Results

A test suite of 19 automated unit tests was executed via `pytest`:
- **Vehicle Physics:** Validated constant speed integration, deceleration boundaries, and highway wrapping.
- **V2V Broker:** Validated Euclidean range cutoff ($d > R \implies$ filtered), simulated latency queuing, sequence gap handling, and stale telemetry tagging.
- **Safety Engine:** Validated TTC calculations for closing, diverging, and zero-relative-speed conditions; verified debounce hysteresis state transitions; validated intersection conflict overlap detection.
- **API & Actuation:** Validated scenario switching, manual emergency brake triggering, and settings validation.

**Result: 19 / 19 tests passed (100% pass rate).**

---

## 7. Limitations and Future Work

1. **2D Local Coordinate Assumption:** Assumes a planar Euclidean surface. Future iterations could incorporate 3D elevation maps and GPS ellipsoid coordinates (WGS84).
2. **RF Channel Modeling:** Currently employs probabilistic packet drop and Gaussian latency jitter. Future enhancements could integrate ray-tracing propagation models accounting for urban buildings and multipath fading.
3. **Autonomous Steer Avoidance:** Currently models longitudinal deceleration. Lateral lane-change collision avoidance maneuvers can be integrated into the vehicle motion model.

---

## 8. Conclusion

SmartV2V successfully delivers an entirely software-based, deterministic, zero-hardware V2V communication and collision warning simulator. By strictly modeling authoritative vehicle physics, cooperative message brokers, standardized safety algorithms, and an intuitive automotive engineering cockpit, the project provides an exceptional practical demonstration of modern Software Defined Vehicle concepts.
