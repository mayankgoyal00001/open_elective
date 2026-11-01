"""
Pre-defined Automotive Simulation Scenarios
Provides deterministic, repeatable test cases for V2V communication,
emergency braking, rear-end risk, intersection conflict, and network degradation.
"""
from typing import Dict, List, Any, Tuple
from app.models.vehicle import VehicleState, VehicleDimensions
from app.core.config import SimulationSettings

class ScenarioManager:
    @staticmethod
    def get_available_scenarios() -> List[Dict[str, Any]]:
        return [
            {
                "id": "normal_traffic",
                "name": "Scenario 1: Normal Highway Traffic",
                "category": "Baseline",
                "description": "Multi-lane highway traffic flowing smoothly. Vehicles maintain safe headway using Intelligent Driver Model (IDM) car-following logic.",
                "expected_outcome": "All vehicles remain in SAFE state. V2V cooperative awareness messages broadcast at 10 Hz with low latency and 0% loss.",
                "is_intersection": False
            },
            {
                "id": "emergency_braking",
                "name": "Scenario 2: Sudden Emergency Braking (EEBL)",
                "category": "Safety Critical",
                "description": "Lead vehicle V2V-01 detects a roadway hazard and performs full-force emergency braking (-8.0 m/s²).",
                "expected_outcome": "Immediate V2V Electronic Emergency Brake Light (EEBL) message transmission. Following vehicles detect risk and alert prior to visual line-of-sight reaction.",
                "is_intersection": False
            },
            {
                "id": "rear_end_risk",
                "name": "Scenario 3: Rear-End Collision Hazard (TTC)",
                "category": "Kinematics",
                "description": "Fast-moving vehicle V2V-02 (115 km/h) approaches slow-moving vehicle V2V-01 (40 km/h) in the same lane.",
                "expected_outcome": "Continuous Time-to-Collision (TTC) evaluation. Warning escalates from SAFE -> WARNING (<4.5s) -> CRITICAL (<2.5s) with distance telemetry.",
                "is_intersection": False
            },
            {
                "id": "intersection_conflict",
                "name": "Scenario 4: 4-Way Intersection Conflict (ICW)",
                "category": "Intersection",
                "description": "Two vehicles approach a blind perpendicular intersection simultaneously without traffic light coordination.",
                "expected_outcome": "Intersection Conflict Warning (ICW) triggered when predicted conflict zone entry times overlap within 1.5 seconds.",
                "is_intersection": True
            },
            {
                "id": "comm_failure",
                "name": "Scenario 5: Degraded Communication & Packet Loss",
                "category": "Cyber-Physical",
                "description": "Adverse RF interference introducing 65% packet loss, 350ms latency, and high jitter.",
                "expected_outcome": "Delayed warning delivery, increased stale telemetry counters, and visual indication of degraded V2V communication health.",
                "is_intersection": False
            }
        ]

    @staticmethod
    def setup_scenario(scenario_id: str, settings: SimulationSettings) -> Tuple[List[VehicleState], bool]:
        """
        Initializes vehicles and network settings for the selected scenario.
        Returns (vehicles, is_intersection_scenario).
        """
        vehicles: List[VehicleState] = []
        is_intersection = False

        if scenario_id == "emergency_braking":
            settings.packet_loss_percent = 0.0
            settings.network_latency_ms = 25.0
            is_intersection = False

            # Lead vehicle emergency braking immediately
            vehicles = [
                VehicleState(
                    vehicle_id="V2V-01",
                    x=240.0,
                    y=20.0,
                    speed_kmh=80.0,
                    speed_ms=22.2,
                    target_speed_ms=0.0,
                    heading=0.0,
                    acceleration=-8.0,
                    braking=True,
                    emergency_braking=True,
                    lane_id=0,
                    color="#EF4444",  # High-alert red
                    driver_profile="aggressive"
                ),
                VehicleState(
                    vehicle_id="V2V-02",
                    x=175.0,
                    y=20.0,
                    speed_kmh=80.0,
                    speed_ms=22.2,
                    target_speed_ms=22.2,
                    heading=0.0,
                    acceleration=0.0,
                    braking=False,
                    emergency_braking=False,
                    lane_id=0,
                    color="#3B82F6"
                ),
                VehicleState(
                    vehicle_id="V2V-03",
                    x=105.0,
                    y=20.0,
                    speed_kmh=78.0,
                    speed_ms=21.6,
                    target_speed_ms=21.6,
                    heading=0.0,
                    acceleration=0.0,
                    braking=False,
                    emergency_braking=False,
                    lane_id=0,
                    color="#10B981"
                ),
                VehicleState(
                    vehicle_id="V2V-04",
                    x=260.0,
                    y=32.0,
                    speed_kmh=90.0,
                    speed_ms=25.0,
                    target_speed_ms=25.0,
                    heading=0.0,
                    acceleration=0.0,
                    braking=False,
                    lane_id=1,
                    color="#8B5CF6"
                ),
                VehicleState(
                    vehicle_id="V2V-05",
                    x=180.0,
                    y=32.0,
                    speed_kmh=88.0,
                    speed_ms=24.4,
                    target_speed_ms=24.4,
                    heading=0.0,
                    acceleration=0.0,
                    braking=False,
                    lane_id=1,
                    color="#06B6D4"
                ),
                VehicleState(
                    vehicle_id="V2V-06",
                    x=100.0,
                    y=32.0,
                    speed_kmh=85.0,
                    speed_ms=23.6,
                    target_speed_ms=23.6,
                    heading=0.0,
                    acceleration=0.0,
                    braking=False,
                    lane_id=1,
                    color="#F59E0B"
                )
            ]

        elif scenario_id == "rear_end_risk":
            settings.packet_loss_percent = 0.0
            settings.network_latency_ms = 20.0
            is_intersection = False

            # Slow leader in lane 0
            vehicles = [
                VehicleState(
                    vehicle_id="V2V-01",
                    x=260.0,
                    y=20.0,
                    speed_kmh=36.0,
                    speed_ms=10.0,
                    target_speed_ms=10.0,
                    heading=0.0,
                    acceleration=0.0,
                    braking=False,
                    lane_id=0,
                    color="#F59E0B"
                ),
                # Fast follower approaching from behind in same lane
                VehicleState(
                    vehicle_id="V2V-02",
                    x=130.0,
                    y=20.0,
                    speed_kmh=115.0,
                    speed_ms=31.9,
                    target_speed_ms=31.9,
                    heading=0.0,
                    acceleration=0.0,
                    braking=False,
                    lane_id=0,
                    color="#EF4444",
                    driver_profile="aggressive"
                ),
                VehicleState(
                    vehicle_id="V2V-03",
                    x=40.0,
                    y=20.0,
                    speed_kmh=70.0,
                    speed_ms=19.4,
                    target_speed_ms=19.4,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=0,
                    color="#10B981"
                ),
                VehicleState(
                    vehicle_id="V2V-04",
                    x=220.0,
                    y=32.0,
                    speed_kmh=90.0,
                    speed_ms=25.0,
                    target_speed_ms=25.0,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=1,
                    color="#8B5CF6"
                ),
                VehicleState(
                    vehicle_id="V2V-05",
                    x=140.0,
                    y=32.0,
                    speed_kmh=88.0,
                    speed_ms=24.4,
                    target_speed_ms=24.4,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=1,
                    color="#06B6D4"
                ),
                VehicleState(
                    vehicle_id="V2V-06",
                    x=60.0,
                    y=32.0,
                    speed_kmh=85.0,
                    speed_ms=23.6,
                    target_speed_ms=23.6,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=1,
                    color="#EC4899"
                )
            ]

        elif scenario_id == "intersection_conflict":
            settings.packet_loss_percent = 0.0
            settings.network_latency_ms = 20.0
            is_intersection = True

            # Center of 4-way intersection is at (300.0, 50.0)
            # Both V2V-01 (Eastbound) and V2V-02 (Northbound) reach center simultaneously in ~6.5s
            vehicles = [
                # Eastbound vehicle along Road 1 (y=50)
                VehicleState(
                    vehicle_id="V2V-01",
                    x=190.0,
                    y=50.0,
                    speed_kmh=61.0,
                    speed_ms=16.94,
                    target_speed_ms=16.94,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=0,
                    color="#EF4444"
                ),
                # Northbound vehicle along Road 2 (x=300)
                VehicleState(
                    vehicle_id="V2V-02",
                    x=300.0,
                    y=-60.0,
                    speed_kmh=61.0,
                    speed_ms=16.94,
                    target_speed_ms=16.94,
                    heading=90.0,
                    acceleration=0.0,
                    lane_id=1,
                    color="#3B82F6"
                ),
                # Trailing vehicle on Eastbound road
                VehicleState(
                    vehicle_id="V2V-03",
                    x=90.0,
                    y=50.0,
                    speed_kmh=54.0,
                    speed_ms=15.0,
                    target_speed_ms=15.0,
                    heading=0.0,
                    lane_id=0,
                    color="#10B981"
                ),
                # Trailing vehicle on Northbound road
                VehicleState(
                    vehicle_id="V2V-04",
                    x=300.0,
                    y=-160.0,
                    speed_kmh=54.0,
                    speed_ms=15.0,
                    target_speed_ms=15.0,
                    heading=90.0,
                    lane_id=1,
                    color="#F59E0B"
                ),
                # Westbound oncoming vehicle
                VehicleState(
                    vehicle_id="V2V-05",
                    x=420.0,
                    y=58.0,
                    speed_kmh=50.0,
                    speed_ms=13.9,
                    target_speed_ms=13.9,
                    heading=180.0,
                    lane_id=2,
                    color="#8B5CF6"
                ),
                # Southbound oncoming vehicle
                VehicleState(
                    vehicle_id="V2V-06",
                    x=308.0,
                    y=170.0,
                    speed_kmh=50.0,
                    speed_ms=13.9,
                    target_speed_ms=13.9,
                    heading=270.0,
                    lane_id=3,
                    color="#06B6D4"
                )
            ]

        elif scenario_id == "comm_failure":
            # Significant wireless packet loss and high latency
            settings.packet_loss_percent = 65.0
            settings.network_latency_ms = 350.0
            settings.stale_message_threshold_s = 0.8
            is_intersection = False

            vehicles = [
                VehicleState(
                    vehicle_id="V2V-01",
                    x=230.0,
                    y=20.0,
                    speed_kmh=75.0,
                    speed_ms=20.8,
                    target_speed_ms=0.0,
                    heading=0.0,
                    acceleration=-6.0,
                    braking=True,
                    emergency_braking=True,
                    lane_id=0,
                    color="#EF4444"
                ),
                VehicleState(
                    vehicle_id="V2V-02",
                    x=160.0,
                    y=20.0,
                    speed_kmh=80.0,
                    speed_ms=22.2,
                    target_speed_ms=22.2,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=0,
                    color="#3B82F6"
                ),
                VehicleState(
                    vehicle_id="V2V-03",
                    x=90.0,
                    y=20.0,
                    speed_kmh=80.0,
                    speed_ms=22.2,
                    target_speed_ms=22.2,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=0,
                    color="#10B981"
                ),
                VehicleState(
                    vehicle_id="V2V-04",
                    x=240.0,
                    y=32.0,
                    speed_kmh=85.0,
                    speed_ms=23.6,
                    target_speed_ms=23.6,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=1,
                    color="#8B5CF6"
                ),
                VehicleState(
                    vehicle_id="V2V-05",
                    x=160.0,
                    y=32.0,
                    speed_kmh=85.0,
                    speed_ms=23.6,
                    target_speed_ms=23.6,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=1,
                    color="#06B6D4"
                ),
                VehicleState(
                    vehicle_id="V2V-06",
                    x=80.0,
                    y=32.0,
                    speed_kmh=80.0,
                    speed_ms=22.2,
                    target_speed_ms=22.2,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=1,
                    color="#F59E0B"
                )
            ]

        else:
            # Baseline: normal_traffic
            settings.packet_loss_percent = 0.0
            settings.network_latency_ms = 20.0
            is_intersection = False

            vehicles = [
                VehicleState(
                    vehicle_id="V2V-01",
                    x=280.0,
                    y=20.0,
                    speed_kmh=80.0,
                    speed_ms=22.2,
                    target_speed_ms=22.2,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=0,
                    color="#3B82F6"
                ),
                VehicleState(
                    vehicle_id="V2V-02",
                    x=190.0,
                    y=20.0,
                    speed_kmh=80.0,
                    speed_ms=22.2,
                    target_speed_ms=22.2,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=0,
                    color="#10B981"
                ),
                VehicleState(
                    vehicle_id="V2V-03",
                    x=90.0,
                    y=20.0,
                    speed_kmh=75.0,
                    speed_ms=20.8,
                    target_speed_ms=20.8,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=0,
                    color="#F59E0B"
                ),
                VehicleState(
                    vehicle_id="V2V-04",
                    x=310.0,
                    y=32.0,
                    speed_kmh=95.0,
                    speed_ms=26.4,
                    target_speed_ms=26.4,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=1,
                    color="#8B5CF6"
                ),
                VehicleState(
                    vehicle_id="V2V-05",
                    x=210.0,
                    y=32.0,
                    speed_kmh=90.0,
                    speed_ms=25.0,
                    target_speed_ms=25.0,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=1,
                    color="#06B6D4"
                ),
                VehicleState(
                    vehicle_id="V2V-06",
                    x=110.0,
                    y=32.0,
                    speed_kmh=88.0,
                    speed_ms=24.4,
                    target_speed_ms=24.4,
                    heading=0.0,
                    acceleration=0.0,
                    lane_id=1,
                    color="#EC4899"
                )
            ]

        # Respect user configured vehicle count if different from 6
        if settings.vehicle_count < len(vehicles):
            vehicles = vehicles[:settings.vehicle_count]

        return vehicles, is_intersection
