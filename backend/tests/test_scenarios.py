"""
Unit Tests for Simulation Scenarios and Engine Lifecycle
"""
import pytest
from app.core.config import SimulationSettings
from app.services.scenario_manager import ScenarioManager
from app.services.simulation_engine import SimulationEngine

def test_available_scenarios():
    scenarios = ScenarioManager.get_available_scenarios()
    assert len(scenarios) == 5
    ids = [s["id"] for s in scenarios]
    assert "normal_traffic" in ids
    assert "emergency_braking" in ids
    assert "rear_end_risk" in ids
    assert "intersection_conflict" in ids
    assert "comm_failure" in ids

def test_scenario_switching_and_reset():
    engine = SimulationEngine(SimulationSettings())
    
    # Load intersection scenario
    engine.load_scenario("intersection_conflict")
    assert engine.is_intersection is True
    assert engine.active_scenario_id == "intersection_conflict"
    assert len(engine.vehicles) >= 2
    
    # Run a few steps
    for _ in range(5):
        engine.step()
    assert engine.sim_time > 0.0
    
    # Reset
    engine.reset()
    assert engine.sim_time == 0.0
    assert engine.active_scenario_id == "intersection_conflict"

def test_engine_metrics_generation():
    engine = SimulationEngine(SimulationSettings())
    engine.load_scenario("normal_traffic")
    
    for _ in range(10):
        engine.step()
        
    metrics = engine.get_metrics()
    assert metrics.active_vehicles == len(engine.vehicles)
    assert metrics.total_messages_sent > 0
    assert metrics.packet_delivery_percentage >= 0.0
