"""
Generate PowerPoint Presentation for SmartV2V Project
Automotive Dark Cockpit Theme (16:9 Widescreen)
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    # Set 16:9 Widescreen Dimensions (13.33 x 7.5 inches)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Theme Colors
    BG_COLOR = RGBColor(11, 15, 25)       # Charcoal Dark
    CARD_BG = RGBColor(19, 27, 46)        # Card Background
    CYAN_ACCENT = RGBColor(6, 182, 212)   # Electric Cyan
    BLUE_ACCENT = RGBColor(59, 130, 246)  # Automotive Blue
    TEXT_MAIN = RGBColor(241, 245, 249)   # Crisp White
    TEXT_MUTED = RGBColor(148, 163, 184)  # Slate Gray
    AMBER = RGBColor(245, 158, 11)        # Warning Amber
    RED = RGBColor(239, 68, 68)           # Alert Red
    GREEN = RGBColor(16, 185, 129)        # Success Green

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.color.rgb = BG_COLOR
        return bg

    def add_header(slide, title_text, category_text="SOFTWARE DEFINED VEHICLE (SDV) CAPSTONE"):
        # Category badge
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = CYAN_ACCENT

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(24)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MAIN

        # Decorative line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.7), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = RGBColor(30, 41, 59)
        line.line.color.rgb = RGBColor(30, 41, 59)

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Badge: Simulation Disclaimer
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.0), Inches(5.8), Inches(0.45))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(69, 26, 3)
    badge.line.color.rgb = AMBER
    p_b = badge.text_frame.paragraphs[0]
    p_b.text = "⚠️ SOFTWARE SIMULATION — NO PHYSICAL VEHICLES CONNECTED"
    p_b.font.size = Pt(9)
    p_b.font.bold = True
    p_b.font.color.rgb = AMBER
    p_b.alignment = PP_ALIGN.CENTER

    # Title text
    t1_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.5), Inches(2.2))
    tf1 = t1_box.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "SmartV2V"
    p1.font.size = Pt(50)
    p1.font.bold = True
    p1.font.color.rgb = CYAN_ACCENT

    p2 = tf1.add_paragraph()
    p2.text = "Software-Based Vehicle-to-Vehicle (V2V) Communication & Collision Warning System"
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_MAIN

    p3 = tf1.add_paragraph()
    p3.text = "A Hardware-Free Cooperative Perception & Forward Collision Avoidance Platform"
    p3.font.size = Pt(14)
    p3.font.color.rgb = TEXT_MUTED

    # Meta card
    meta = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.5), Inches(11.7), Inches(1.8))
    meta.fill.solid()
    meta.fill.fore_color.rgb = CARD_BG
    meta.line.color.rgb = RGBColor(30, 41, 59)
    
    tf_m = meta.text_frame
    tf_m.word_wrap = True
    pm1 = tf_m.paragraphs[0]
    pm1.text = "PROJECT METADATA & ACADEMIC CONTEXT"
    pm1.font.size = Pt(11)
    pm1.font.bold = True
    pm1.font.color.rgb = BLUE_ACCENT

    pm2 = tf_m.add_paragraph()
    pm2.text = "• Course / Domain: Software Defined Vehicles (SDV) | Intelligent Transportation Systems (ITS)"
    pm2.font.size = Pt(11)
    pm2.font.color.rgb = TEXT_MAIN

    pm3 = tf_m.add_paragraph()
    pm3.text = "• Technology Stack: Python FastAPI (20 Hz Engine) • WebSockets • React + Vite + TypeScript • HTML5 Canvas"
    pm3.font.size = Pt(11)
    pm3.font.color.rgb = TEXT_MAIN

    pm4 = tf_m.add_paragraph()
    pm4.text = "• Standards Modeled: SAE J2735 Basic Safety Message (BSM) • ETSI CAM • ISO 15623 Forward Collision Warning"
    pm4.font.size = Pt(11)
    pm4.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 2: Problem Statement & Motivation
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Problem Statement & Industry Motivation")

    # 3 Column Cards
    col_width = Inches(3.7)
    cards_data = [
        ("1. Line-of-Sight Sensor Limits", [
            "Current ADAS (cameras, radar, lidar) rely strictly on direct line-of-sight.",
            "Occlusions (large trucks, blind curves, fog, heavy rain) conceal braking hazards ahead.",
            "Sensors cannot perceive intent before mechanical deceleration occurs."
        ], RED),
        ("2. Driver Reaction Delay", [
            "Average human brake reaction delay is 1.0 to 1.5 seconds.",
            "At 100 km/h highway speed, a vehicle travels 28 to 42 meters before the driver even taps the brake pedal.",
            "Cooperative V2V broadcasts intent in milliseconds at light speed."
        ], AMBER),
        ("3. High Cost of Physical Testbeds", [
            "Physical DSRC / C-V2X radio hardware, ESP32 rigs, and test vehicles cost thousands of dollars.",
            "Difficult to reproduce deterministic edge-case collision scenarios safely.",
            "Need for a robust 100% software simulation running locally on a standard laptop."
        ], CYAN_ACCENT)
    ]

    for i, (ctitle, cbullets, ccolor) in enumerate(cards_data):
        cx = Inches(0.8 + i * 4.0)
        cbox = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, Inches(1.8), col_width, Inches(4.8))
        cbox.fill.solid()
        cbox.fill.fore_color.rgb = CARD_BG
        cbox.line.color.rgb = RGBColor(30, 41, 59)
        
        tf = cbox.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = ctitle
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = ccolor

        for b in cbullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.size = Pt(11)
            pb.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 3: Project Objectives & Core Constraints
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Project Objectives & Technical Scope")

    # Left Card: Objectives
    o_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.8))
    o_box.fill.solid()
    o_box.fill.fore_color.rgb = CARD_BG
    o_box.line.color.rgb = RGBColor(30, 41, 59)
    tf_o = o_box.text_frame
    tf_o.word_wrap = True
    p = tf_o.paragraphs[0]
    p.text = "PRIMARY SYSTEM OBJECTIVES"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    objs = [
        "Software-Only Cooperative V2V Simulator: Demonstrates multi-vehicle communication and forward collision risk anticipation.",
        "Authoritative 20 Hz Kinematic Engine: Numerical integration of vehicle motion, speed regulation, and safe spacing.",
        "Full Wireless Cyber-Physical Broker: Euclidean range filtering, simulated packet loss, and latency queuing.",
        "Multi-Rule Safety Suite: Calculates real-time Time-to-Collision (TTC), Forward Collision Warning (FCW), Emergency Electronic Brake Light (EEBL), and Intersection Conflict Warning (ICW).",
        "Cockpit-Grade Dashboard: High-contrast dark automotive engineering monitor with Retina 2D canvas, charts, and packet decoders."
    ]
    for b in objs:
        pb = tf_o.add_paragraph()
        pb.text = f"✔ {b}"
        pb.font.size = Pt(11)
        pb.font.color.rgb = TEXT_MAIN

    # Right Card: Constraints
    c_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = CARD_BG
    c_box.line.color.rgb = RGBColor(30, 41, 59)
    tf_c = c_box.text_frame
    tf_c.word_wrap = True
    p = tf_c.paragraphs[0]
    p.text = "IMPORTANT PROJECT CONSTRAINTS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = AMBER

    cons = [
        "100% Software-Based: Zero physical microcontrollers (ESP32 / Arduino / Raspberry Pi) or hardware radio transceivers.",
        "Local Execution: Runs completely offline on a normal consumer laptop without external server dependencies.",
        "Zero Paid APIs / Keys: Does not require Google Maps, Mapbox, or external telematics cloud subscriptions.",
        "Local 2D Road Visualization: Native HTML5 Canvas road rendering that works reliably without internet tile downloads.",
        "Functional State Engine: Not a static UI mockup — authoritative Python physics loop governs the real-time simulation."
    ]
    for b in cons:
        pb = tf_c.add_paragraph()
        pb.text = f"⚡ {b}"
        pb.font.size = Pt(11)
        pb.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 4: System Architecture (SDV Paradigm)
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Software Defined Vehicle (SDV) Architecture")

    arch_layers = [
        ("Layer 1: Automotive Cockpit UI", "React 18 • TypeScript • Tailwind CSS • Lucide Icons • Recharts\n• TopNav Status & Clocks • Summary Telemetry Cards • Live Safety Event Feed\n• HTML5 Retina 2D Road Canvas (Highway Corridor & 4-Way Intersection Grid)", CYAN_ACCENT),
        ("Layer 2: Transport & API Gateway", "FastAPI • WebSockets (20 Hz Full State Stream) • REST Endpoints\n• Non-blocking client broadcasts • Instant actuation commands (Manual Emergency Brake)", BLUE_ACCENT),
        ("Layer 3: Authoritative Simulation Engine", "Python asyncio (20 Hz Physics Loop, dt = 0.05s)\n• Kinematics Numerical Integration • Car-Following Spacing • Speed Multiplier Control", GREEN),
        ("Layer 4: Cyber-Physical V2V Broker", "In-Memory SAE J2735 Basic Safety Message (BSM) Broker\n• Euclidean Range Filter (d <= R_comm) • Delayed Transit Queue (Network Latency) • Packet Loss Probability", AMBER),
        ("Layer 5: Collision Safety Engine", "Rule-Based Safety Evaluation with Stateful Debounce Hysteresis\n• Time-to-Collision (TTC) • Forward Collision Warning (FCW) • Emergency Brake (EEBL) • Intersection Conflict (ICW)", RED),
    ]

    for i, (ltitle, ldesc, lcolor) in enumerate(arch_layers):
        ly = Inches(1.8 + i * 1.0)
        lbox = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), ly, Inches(11.7), Inches(0.85))
        lbox.fill.solid()
        lbox.fill.fore_color.rgb = CARD_BG
        lbox.line.color.rgb = lcolor
        
        tf = lbox.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = ltitle
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = lcolor

        pd = tf.add_paragraph()
        pd.text = ldesc
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 5: V2V Communication Protocol & Modeling
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Simulated V2V Communication Protocol (SAE J2735)")

    # Left: Packet Format
    pkt_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.8))
    pkt_box.fill.solid()
    pkt_box.fill.fore_color.rgb = CARD_BG
    pkt_box.line.color.rgb = RGBColor(30, 41, 59)
    tf_p = pkt_box.text_frame
    tf_p.word_wrap = True
    p = tf_p.paragraphs[0]
    p.text = "BASIC SAFETY MESSAGE (BSM) SCHEMA"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    schema_fields = [
        "message_id: Unique packet identifier (e.g., MSG-V2V-01-42)",
        "sender_id: Transmitting vehicle ID node",
        "sequence_number: Monotonically increasing sequence tracker",
        "timestamp: Simulation time of transmission (seconds)",
        "position_x, position_y: Real coordinates in meters",
        "speed_kmh, speed_ms: Forward velocity telemetry",
        "heading: Orientation in degrees (0° East, 90° North)",
        "acceleration: Longitudinal acceleration in m/s²",
        "brake_active: Mechanical brake pedal status (Boolean)",
        "emergency_brake_active: Electronic Emergency Brake Light (EEBL)",
        "event_flags: ['EMERGENCY_BRAKE_ACTIVE', 'HARD_DECELERATION']"
    ]
    for sf in schema_fields:
        psf = tf_p.add_paragraph()
        psf.text = f"• {sf}"
        psf.font.size = Pt(10)
        psf.font.color.rgb = TEXT_MAIN

    # Right: Channel Modeling
    chan_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    chan_box.fill.solid()
    chan_box.fill.fore_color.rgb = CARD_BG
    chan_box.line.color.rgb = RGBColor(30, 41, 59)
    tf_ch = chan_box.text_frame
    tf_ch.word_wrap = True
    p = tf_ch.paragraphs[0]
    p.text = "WIRELESS CHANNEL & BROKER LOGIC"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT

    chan_points = [
        "Euclidean Range Filtering: d = sqrt((x1-x2)² + (y1-y2)²). If d > R_comm (default 200m), packet is dropped (out of radio reach).",
        "Simulated Propagation & Queue Latency: Scheduled delivery at t_deliver = t_sent + latency_ms * jitter (default 20ms ± 10%).",
        "Packet Loss Simulation: Configurable RF drop probability (0% to 80%). Simulates multipath fading & wireless channel interference.",
        "Per-Vehicle Reception Tables: Each node maintains an internal cooperative state table of all neighbor nodes.",
        "Freshness Checks: If time since sender broadcast > 0.8s, packet is flagged as STALE, signaling degraded V2V link health."
    ]
    for cp in chan_points:
        pcp = tf_ch.add_paragraph()
        pcp.text = f"• {cp}"
        pcp.font.size = Pt(10.5)
        pcp.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 6: Collision Safety Engine & Mathematics
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Safety Engine Formulations & Collision Detection")

    math_box1 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.8))
    math_box1.fill.solid()
    math_box1.fill.fore_color.rgb = CARD_BG
    math_box1.line.color.rgb = RGBColor(30, 41, 59)
    tf1 = math_box1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "FEATURE A: TIME-TO-COLLISION (TTC)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    ttc_content = [
        "Net Longitudinal Clearance:",
        "  d_clear = x_leader - x_follower - L_vehicle  (L = 4.8m)",
        "Relative Closing Velocity:",
        "  v_closing = v_follower - v_leader",
        "Mathematical TTC Projection:",
        "  TTC = d_clear / v_closing   (if v_closing > 0.1 m/s)",
        "ISO 15623 Alert Thresholds:",
        "  • CRITICAL: TTC <= 2.5s (Imminent crash trajectory)",
        "  • WARNING: 2.5s < TTC <= 4.5s (Safe braking threshold)",
        "  • SAFE: TTC > 4.5s or v_closing <= 0 (Diverging vehicles)"
    ]
    for tc in ttc_content:
        ptc = tf1.add_paragraph()
        ptc.text = tc
        ptc.font.size = Pt(10)
        ptc.font.color.rgb = TEXT_MAIN

    math_box2 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    math_box2.fill.solid()
    math_box2.fill.fore_color.rgb = CARD_BG
    math_box2.line.color.rgb = RGBColor(30, 41, 59)
    tf2 = math_box2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "FEATURES B, C & D: EEBL, ICW & DEBOUNCE"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = AMBER

    other_content = [
        "Electronic Emergency Brake Light (EEBL):",
        "  • Triggered when deceleration a <= -4.5 m/s² or manual trigger.",
        "  • In-lane followers receive V2V packet and trigger CRITICAL alert before visual detection.",
        "Intersection Conflict Warning (ICW):",
        "  • Evaluates perpendicular crossing trajectories (East-West vs North-South).",
        "  • Conflict overlap: delta_t = |T_enter_EW - T_enter_NS|.",
        "  • delta_t < 1.2s -> CRITICAL simultaneous arrival alert.",
        "Stateful Hysteresis Debouncer:",
        "  • Requires 2 consecutive cycles to escalate alert level.",
        "  • Requires 3 consecutive safe cycles to drop alert.",
        "  • Eliminates high-frequency warning flickering near boundaries."
    ]
    for oc in other_content:
        poc = tf2.add_paragraph()
        poc.text = oc
        poc.font.size = Pt(10)
        poc.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 7: The 5 Pre-Defined Simulation Scenarios
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Interactive Simulation Scenarios (Repeatable & Deterministic)")

    scenarios = [
        ("Scenario 1: Normal Highway Traffic", "Baseline: Multi-lane cruising with IDM safe headway spacing.", "All vehicles remain in SAFE state. 100% packet delivery ratio at 10 Hz broadcast.", GREEN),
        ("Scenario 2: Sudden Emergency Braking (EEBL)", "Safety Critical: Lead vehicle V2V-01 detects hazard, brakes at -8.5 m/s².", "Immediate V2V EEBL broadcast. Follower V2V-02 alerts critically prior to driver reaction.", RED),
        ("Scenario 3: Rear-End Collision Hazard (TTC)", "Kinematics: Fast vehicle (115 km/h) approaches slow vehicle (40 km/h).", "Demonstrates smooth TTC evaluation escalating from SAFE -> WARNING -> CRITICAL (<2.5s).", AMBER),
        ("Scenario 4: 4-Way Intersection Conflict (ICW)", "Intersection: Blind perpendicular crossing arrival at (300m, 50m).", "Conflict zone overlap < 1.2s triggers simultaneous CRITICAL Intersection Warning.", CYAN_ACCENT),
        ("Scenario 5: Communication Failure", "Cyber-Physical: 65% packet loss and 350ms latency introduced.", "Demonstrates degraded delivery ratio, stale packet counts, and delayed warning alerts.", RGBColor(168, 85, 247))
    ]

    for i, (stitle, sdesc, soutcome, scolor) in enumerate(scenarios):
        sy = Inches(1.8 + i * 1.0)
        sbox = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), sy, Inches(11.7), Inches(0.88))
        sbox.fill.solid()
        sbox.fill.fore_color.rgb = CARD_BG
        sbox.line.color.rgb = scolor
        
        tf = sbox.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = stitle
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = scolor

        pd = tf.add_paragraph()
        pd.text = f"Setup: {sdesc} | Outcome: {soutcome}"
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 8: Automotive Cockpit UI & Visualization
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Cockpit Dashboard & Visualization Features")

    dash_features = [
        ("Local 2D Road Canvas", [
            "Native HTML5 Canvas with device-pixel-ratio Retina scaling.",
            "Multi-lane horizontal highway corridor with dashed markings & distance ticks (0-600m).",
            "4-Way intersection conflict zone with yellow crosshatch markings & stop lines.",
            "Vehicle markers show speed tags, ID badges, front headlights, and red brake light flares.",
            "Pulsing cyan V2V wireless link lines & flashing red/amber collision vectors with TTC labels."
        ]),
        ("Summary Cards & Real-Time Curves", [
            "6 Live KPI Cards: Active Vehicles, V2V Msg/s, Collision Warnings, Critical Alerts, Latency, Delivery Ratio.",
            "Recharts Real-time Curves: Vehicle speed profiles over time, collision warning counts, V2V broadcast rate (Hz), and network latency (ms).",
            "Auto-scrolling Live Event Feed filterable by severity (Critical, Warning, Info)."
        ]),
        ("Vehicle Telemetry Drawer & Actuators", [
            "Click any vehicle to inspect speed, acceleration, heading, coordinates, and nearby nodes.",
            "Received BSM table displaying decoded neighbor packets, latency, and freshness badges.",
            "Prominent 'TRIGGER EMERGENCY BRAKE' button to inject physical braking deceleration."
        ]),
        ("Protocol & Network Analytics Modals", [
            "BSM Packet Inspector: Searchable live stream of transmitted packets with raw decoded JSON.",
            "Network Analytics Modal: QoS delivery ratio, packet drop breakdown, and per-vehicle matrix.",
            "Settings Modal: Live tuning of speed factor, vehicle density, range, loss %, and latency."
        ])
    ]

    for i, (dtitle, dbullets) in enumerate(dash_features):
        r = i // 2
        c = i % 2
        dx = Inches(0.8 + c * 6.0)
        dy = Inches(1.8 + r * 2.5)

        dbox = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, dx, dy, Inches(5.7), Inches(2.35))
        dbox.fill.solid()
        dbox.fill.fore_color.rgb = CARD_BG
        dbox.line.color.rgb = RGBColor(30, 41, 59)
        
        tf = dbox.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = dtitle
        pt.font.size = Pt(11.5)
        pt.font.bold = True
        pt.font.color.rgb = CYAN_ACCENT

        for b in dbullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.size = Pt(9.5)
            pb.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 9: Testing & Verification Results
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Verification & Automated Test Suite Results")

    # Left: Test Summary Stats
    tstat_box = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8))
    tstat_box.fill.solid()
    tstat_box.fill.fore_color.rgb = CARD_BG
    tstat_box.line.color.rgb = GREEN
    tf_ts = tstat_box.text_frame
    tf_ts.word_wrap = True
    p = tf_ts.paragraphs[0]
    p.text = "TEST SUITE SUMMARY"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GREEN

    tstats = [
        "Frameworks:",
        "  • Pytest + Starlette TestClient",
        "  • Vitest + Testing Library",
        "Automated Unit Tests:",
        "  • 19 Backend Tests (100% Pass)",
        "  • 1 Frontend Component Test",
        "Execution Time:",
        "  • 0.95 seconds total",
        "Production Bundle:",
        "  • Vite 6 build: 7.07s clean",
        "Status: VERIFIED 100%"
    ]
    for ts in tstats:
        pts = tf_ts.add_paragraph()
        pts.text = ts
        pts.font.size = Pt(10)
        pts.font.color.rgb = TEXT_MAIN

    # Right: Verified Test Categories
    tcat_box = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.7), Inches(1.8), Inches(7.8), Inches(4.8))
    tcat_box.fill.solid()
    tcat_box.fill.fore_color.rgb = CARD_BG
    tcat_box.line.color.rgb = RGBColor(30, 41, 59)
    tf_tc = tcat_box.text_frame
    tf_tc.word_wrap = True
    p = tf_tc.paragraphs[0]
    p.text = "TESTED MODULES & EDGE CASES"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT

    tcats = [
        "1. Vehicle Kinematics Integration: Verified constant speed dx integration, emergency deceleration (-8.5 m/s²), and highway boundary wrap-around.",
        "2. Range Filtering: Confirmed vehicles beyond Euclidean cutoff (e.g. 150m > 100m) are strictly excluded from transmission queue.",
        "3. Transmission Queue & Latency: Verified packets remain in transit until simulated latency elapsed (e.g. 50ms) before entering received tables.",
        "4. Stale Telemetry Detection: Verified age expiration (>0.5s) correctly flags packets as STALE in reception records.",
        "5. TTC Calculation Edge Cases: Tested closing velocity >0, diverging velocity (None), zero relative speed (None), and contact overlap (0.0s).",
        "6. Hysteresis Debouncing: Confirmed 2-cycle escalation filter prevents transient noise from triggering false alarms.",
        "7. Intersection Conflict: Validated simultaneous arrival time-overlap calculation at (300m, 50m).",
        "8. REST & Actuation Endpoints: Verified status snapshots, scenario switching, settings updates, and emergency brake actuators."
    ]
    for tc in tcats:
        ptc = tf_tc.add_paragraph()
        ptc.text = tc
        ptc.font.size = Pt(9.5)
        ptc.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 10: Conclusion & Key Learnings
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Conclusions & SDV Capstone Takeaways")

    c1 = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.8))
    c1.fill.solid()
    c1.fill.fore_color.rgb = CARD_BG
    c1.line.color.rgb = GREEN
    tf_c1 = c1.text_frame
    tf_c1.word_wrap = True
    p = tf_c1.paragraphs[0]
    p.text = "KEY PROJECT ACHIEVEMENTS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GREEN

    achievements = [
        "100% Software-Based Realization: Proved that complex automotive V2V workflows and forward collision avoidance can be modeled realistically without expensive hardware.",
        "Cooperative Perception Supremacy: Demonstrated that V2V EEBL alerts vehicles before visual reaction delay, dramatically expanding the safe stopping window.",
        "SDV Architectural Rigor: Clean separation of Authoritative Physics (20 Hz loop), Cyber-Physical Communication Broker, Rule-Based Safety Engine, and Cockpit UI.",
        "Reproducible Experimental Testbed: 5 deterministic scenarios allow repeatable demonstration of baseline flow, brake hazards, TTC escalation, and packet loss.",
        "Professional Engineering Cockpit: Delivers an intuitive, automotive-grade dark UI rather than a generic admin template."
    ]
    for a in achievements:
        pa = tf_c1.add_paragraph()
        pa.text = f"✔ {a}"
        pa.font.size = Pt(10.5)
        pa.font.color.rgb = TEXT_MAIN

    c2 = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    c2.fill.solid()
    c2.fill.fore_color.rgb = CARD_BG
    c2.line.color.rgb = BLUE_ACCENT
    tf_c2 = c2.text_frame
    tf_c2.word_wrap = True
    p = tf_c2.paragraphs[0]
    p.text = "LIMITATIONS & FUTURE ENHANCEMENTS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT

    future = [
        "3D Terrain & Road Curvature: Extend 2D planar coordinates to 3D elevation maps with true WGS84 GPS ellipsoid positioning.",
        "Physical Multipath Ray-Tracing: Replace statistical packet loss with 3D ray-tracing radio propagation models accounting for urban buildings.",
        "Active Autonomous Evasive Maneuvers: Implement automated steering and cooperative lane-change maneuvers in response to EEBL warnings.",
        "V2X Infrastructure (V2I): Model intelligent traffic signal controllers (SPaT messages) communicating signal phase timing to approaching vehicles.",
        "Hardware-in-the-Loop (HIL) Bridge: Optional socket bridge to interface real ESP32 / CAN-bus nodes in future lab work."
    ]
    for f in future:
        pf = tf_c2.add_paragraph()
        pf.text = f"🚀 {f}"
        pf.font.size = Pt(10.5)
        pf.font.color.rgb = TEXT_MAIN

    # Save presentation file
    output_path = os.path.abspath("SmartV2V_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation successfully created at: {output_path}")

if __name__ == "__main__":
    create_presentation()
