"""
Unit Tests for FastAPI REST Endpoints and Actuation
"""
import pytest
from starlette.testclient import TestClient
from main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "SmartV2V" in data["service"]

def test_api_simulation_status():
    res = client.get("/api/simulation/status")
    assert res.status_code == 200
    data = res.json()
    assert "vehicles" in data
    assert "metrics" in data
    assert "recent_events" in data

def test_api_vehicles_list_and_detail():
    res = client.get("/api/vehicles")
    assert res.status_code == 200
    vehicles = res.json()
    assert len(vehicles) >= 2
    
    first_id = vehicles[0]["vehicle_id"]
    res_single = client.get(f"/api/vehicles/{first_id}")
    assert res_single.status_code == 200
    assert res_single.json()["vehicle_id"] == first_id

def test_api_scenario_switch():
    res = client.post("/api/simulation/scenario", json={"scenario_id": "emergency_braking"})
    assert res.status_code == 200
    assert res.json()["scenario_id"] == "emergency_braking"

def test_api_emergency_brake_actuation():
    res = client.post("/api/vehicles/V2V-01/emergency-brake")
    assert res.status_code == 200
    assert res.json()["action"] == "EMERGENCY_BRAKE_TRIGGERED"

def test_api_settings_update():
    res = client.post("/api/simulation/settings", json={"packet_loss_percent": 15.0, "network_latency_ms": 45.0})
    assert res.status_code == 200
    settings = res.json()["settings"]
    assert settings["packet_loss_percent"] == 15.0
    assert settings["network_latency_ms"] == 45.0
