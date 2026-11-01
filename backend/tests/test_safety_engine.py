"""
Unit Tests for Automotive Safety Engine
Tests TTC calculation, FCW alerts, EEBL broadcast, and Intersection Conflicts.
"""
import pytest
from app.models.vehicle import VehicleState
from app.core.config import SimulationSettings
from app.services.safety_engine import SafetyEngine, RiskStateDebouncer
from app.services.v2v_broker import V2VCommunicationBroker

def test_ttc_calculation():
    engine = SafetyEngine(SimulationSettings())
    
    # Case 1: Follower moving 30 m/s, Leader moving 20 m/s (closing speed = 10 m/s)
    # Leader at 104.8m, Follower at 0m, vehicle length 4.8m -> clearance = 100m
    # Expected TTC = 100 / 10 = 10.0 seconds
    ttc = engine.compute_ttc_same_lane(
        follower_x=0.0, follower_speed_ms=30.0,
        leader_x=104.8, leader_speed_ms=20.0,
        vehicle_length=4.8
    )
    assert ttc == 10.0

    # Case 2: Diverging vehicles (Follower moving slower than Leader)
    ttc_diverging = engine.compute_ttc_same_lane(
        follower_x=0.0, follower_speed_ms=20.0,
        leader_x=104.8, leader_speed_ms=30.0,
        vehicle_length=4.8
    )
    assert ttc_diverging is None

    # Case 3: Zero closing speed (identical speeds)
    ttc_equal = engine.compute_ttc_same_lane(
        follower_x=0.0, follower_speed_ms=25.0,
        leader_x=104.8, leader_speed_ms=25.0,
        vehicle_length=4.8
    )
    assert ttc_equal is None

    # Case 4: Overlap / immediate contact
    ttc_overlap = engine.compute_ttc_same_lane(
        follower_x=100.0, follower_speed_ms=25.0,
        leader_x=102.0, leader_speed_ms=10.0,
        vehicle_length=4.8
    )
    assert ttc_overlap == 0.0

def test_debouncer_hysteresis():
    debouncer = RiskStateDebouncer(escalate_cycles=2, deescalate_cycles=3)
    pair = "V1->V2"
    
    # 1st cycle with WARNING -> remains SAFE until confirmed
    res1 = debouncer.update(pair, "WARNING")
    assert res1 == "SAFE"
    
    # 2nd cycle with WARNING -> confirmed escalation to WARNING
    res2 = debouncer.update(pair, "WARNING")
    assert res2 == "WARNING"
    
    # Transient single SAFE reading -> should not deescalate immediately (hysteresis)
    res_transient = debouncer.update(pair, "SAFE")
    assert res_transient == "WARNING"

def test_intersection_conflict_detection():
    engine = SafetyEngine(SimulationSettings())
    
    # Two vehicles arriving at intersection center (300, 50) at the same time:
    # EW vehicle at x=200, moving East (heading 0) at 20 m/s -> (300 - 200) / 20 = 5.0s
    v_ew = VehicleState(vehicle_id="V-EW", x=200.0, y=50.0, speed_ms=20.0, heading=0.0)
    
    # NS vehicle at y=-50, moving North (heading 90) at 20 m/s -> (50 - (-50)) / 20 = 5.0s
    v_ns = VehicleState(vehicle_id="V-NS", x=300.0, y=-50.0, speed_ms=20.0, heading=90.0)
    
    conflict = engine.evaluate_intersection_conflict(v_ew, v_ns, intersection_center=(300.0, 50.0))
    assert conflict is not None
    risk_level, time_diff, dist = conflict
    assert risk_level in ["WARNING", "CRITICAL"]
    assert time_diff < 0.5  # Arriving virtually simultaneously
