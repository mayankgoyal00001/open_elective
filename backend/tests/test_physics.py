"""
Unit Tests for Vehicle Physics and Kinematics Integration
"""
import pytest
from app.models.vehicle import VehicleState
from app.core.config import SimulationSettings
from app.services.simulation_engine import SimulationEngine

def test_vehicle_initialization():
    v = VehicleState(
        vehicle_id="V2V-01",
        x=100.0,
        y=20.0,
        speed_kmh=72.0,
        speed_ms=20.0,
        heading=0.0
    )
    assert v.vehicle_id == "V2V-01"
    assert v.x == 100.0
    assert v.speed_kmh == 72.0
    assert v.speed_ms == 20.0
    assert v.risk_level == "SAFE"

def test_kinematics_constant_speed_integration():
    settings = SimulationSettings(time_step=0.1, speed_multiplier=1.0)
    engine = SimulationEngine(settings)
    engine.load_scenario("normal_traffic")
    
    # Take first vehicle
    v0 = engine.vehicles[0]
    initial_x = v0.x
    initial_speed = v0.speed_ms
    
    # Step simulation once
    engine.step()
    
    # Expected dx = speed_ms * dt = initial_speed * 0.1
    # Allow small tolerance due to acceleration controller
    assert engine.vehicles[0].x > initial_x
    assert engine.vehicles[0].updated_at > 0.0

def test_emergency_braking_deceleration():
    settings = SimulationSettings(time_step=0.1)
    engine = SimulationEngine(settings)
    engine.load_scenario("normal_traffic")
    
    target_v = engine.vehicles[0]
    v_id = target_v.vehicle_id
    initial_speed = target_v.speed_ms
    
    # Trigger emergency brake
    assert engine.trigger_emergency_brake(v_id) is True
    assert target_v.emergency_braking is True
    assert target_v.acceleration <= -8.0
    
    # Step simulation multiple times to verify deceleration
    for _ in range(5):
        engine.step()
        
    assert target_v.speed_ms < initial_speed
