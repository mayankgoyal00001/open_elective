"""
REST API Endpoints for SmartV2V
Exposes control, state query, scenario configuration, and vehicle actuation.
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field

from app.models.vehicle import VehicleState, VehicleTelemetryUpdate
from app.models.event import SafetyEvent
from app.models.metrics import SimulationMetrics
from app.models.message import ReceivedMessageRecord, NetworkTransmissionLog
from app.core.config import SimulationSettings
from app.services.simulation_engine import SimulationEngine
from app.services.scenario_manager import ScenarioManager

router = APIRouter(prefix="/api", tags=["SmartV2V Automotive Platform"])

# Global simulation instance will be set by main.py
sim_engine: Optional[SimulationEngine] = None

def get_engine() -> SimulationEngine:
    if sim_engine is None:
        raise HTTPException(status_code=500, detail="Simulation Engine is not initialized")
    return sim_engine

class ScenarioSelectRequest(BaseModel):
    scenario_id: str = Field(..., description="ID of scenario to load (e.g. normal_traffic, emergency_braking)")

class SettingsUpdateRequest(BaseModel):
    speed_multiplier: Optional[float] = Field(None, ge=0.1, le=5.0)
    vehicle_count: Optional[int] = Field(None, ge=2, le=16)
    communication_range_m: Optional[float] = Field(None, ge=30.0, le=600.0)
    message_frequency_hz: Optional[float] = Field(None, ge=1.0, le=25.0)
    packet_loss_percent: Optional[float] = Field(None, ge=0.0, le=80.0)
    network_latency_ms: Optional[float] = Field(None, ge=0.0, le=500.0)

# 1. Health
@router.get("/health")
def get_health():
    return {
        "status": "healthy",
        "service": "SmartV2V Simulation & Collision Warning Platform",
        "version": "1.0.0",
        "architecture": "Software Defined Vehicle (SDV) Automotive Simulation"
    }

# 2. Simulation Status & Full Snapshot
@router.get("/simulation/status")
def get_simulation_status(engine: SimulationEngine = Depends(get_engine)):
    return engine.get_full_state_snapshot()

# 3. Vehicle List
@router.get("/vehicles", response_model=List[VehicleState])
def get_vehicles(engine: SimulationEngine = Depends(get_engine)):
    return engine.vehicles

# 4. Vehicle Detail
@router.get("/vehicles/{vehicle_id}", response_model=VehicleState)
def get_vehicle_by_id(vehicle_id: str, engine: SimulationEngine = Depends(get_engine)):
    for v in engine.vehicles:
        if v.vehicle_id == vehicle_id:
            return v
    raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")

# 5. Vehicle Received Messages (Inspector)
@router.get("/vehicles/{vehicle_id}/messages")
def get_vehicle_messages(vehicle_id: str, engine: SimulationEngine = Depends(get_engine)):
    rec_table = engine.v2v_broker.received_tables.get(vehicle_id, {})
    return {
        "vehicle_id": vehicle_id,
        "received_messages": {s_id: rec.model_dump() for s_id, rec in rec_table.items()}
    }

# 6. Safety Events
@router.get("/events", response_model=List[SafetyEvent])
def get_recent_events(limit: int = 50, engine: SimulationEngine = Depends(get_engine)):
    events = list(engine.recent_events)
    return events[-limit:]

# 7. Metrics
@router.get("/metrics", response_model=SimulationMetrics)
def get_simulation_metrics(engine: SimulationEngine = Depends(get_engine)):
    return engine.get_metrics()

# 8. Available Scenarios
@router.get("/scenarios")
def get_scenarios():
    return ScenarioManager.get_available_scenarios()

# 9. Message Transmission Logs
@router.get("/messages/logs", response_model=List[NetworkTransmissionLog])
def get_message_logs(limit: int = 50, engine: SimulationEngine = Depends(get_engine)):
    logs = list(engine.v2v_broker.transmission_logs)
    return logs[-limit:]

# Controls: Start
@router.post("/simulation/start")
async def start_simulation(engine: SimulationEngine = Depends(get_engine)):
    await engine.start()
    return {"status": engine.status, "message": "Simulation started"}

# Controls: Pause
@router.post("/simulation/pause")
async def pause_simulation(engine: SimulationEngine = Depends(get_engine)):
    await engine.pause()
    return {"status": engine.status, "message": "Simulation paused"}

# Controls: Resume
@router.post("/simulation/resume")
async def resume_simulation(engine: SimulationEngine = Depends(get_engine)):
    await engine.resume()
    return {"status": engine.status, "message": "Simulation resumed"}

# Controls: Stop
@router.post("/simulation/stop")
async def stop_simulation(engine: SimulationEngine = Depends(get_engine)):
    await engine.stop()
    return {"status": engine.status, "message": "Simulation stopped"}

# Controls: Reset
@router.post("/simulation/reset")
def reset_simulation(engine: SimulationEngine = Depends(get_engine)):
    engine.reset()
    return {"status": engine.status, "sim_time": engine.sim_time, "message": "Simulation reset successfully"}

# Controls: Select Scenario
@router.post("/simulation/scenario")
def set_scenario(req: ScenarioSelectRequest, engine: SimulationEngine = Depends(get_engine)):
    valid_ids = [s["id"] for s in ScenarioManager.get_available_scenarios()]
    if req.scenario_id not in valid_ids:
        raise HTTPException(status_code=400, detail=f"Invalid scenario ID. Valid options: {valid_ids}")
    engine.load_scenario(req.scenario_id)
    return {
        "status": engine.status,
        "scenario_id": engine.active_scenario_id,
        "is_intersection": engine.is_intersection,
        "message": f"Switched to scenario: {req.scenario_id}"
    }

# Controls: Update Settings
@router.post("/simulation/settings")
def update_settings(req: SettingsUpdateRequest, engine: SimulationEngine = Depends(get_engine)):
    if req.speed_multiplier is not None:
        engine.settings.speed_multiplier = req.speed_multiplier
    if req.vehicle_count is not None:
        engine.settings.vehicle_count = req.vehicle_count
    if req.communication_range_m is not None:
        engine.settings.communication_range_m = req.communication_range_m
    if req.message_frequency_hz is not None:
        engine.settings.message_frequency_hz = req.message_frequency_hz
    if req.packet_loss_percent is not None:
        engine.settings.packet_loss_percent = req.packet_loss_percent
    if req.network_latency_ms is not None:
        engine.settings.network_latency_ms = req.network_latency_ms

    return {
        "message": "Simulation settings updated",
        "settings": engine.settings.model_dump()
    }

# Actuation: Manual Emergency Braking
@router.post("/vehicles/{vehicle_id}/emergency-brake")
def trigger_vehicle_emergency_brake(vehicle_id: str, engine: SimulationEngine = Depends(get_engine)):
    success = engine.trigger_emergency_brake(vehicle_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")
    return {
        "vehicle_id": vehicle_id,
        "action": "EMERGENCY_BRAKE_TRIGGERED",
        "deceleration": -8.5,
        "message": f"Emergency braking engaged on {vehicle_id}"
    }

# Actuation: Telemetry Update
@router.post("/vehicles/{vehicle_id}/telemetry")
def update_vehicle_telemetry(vehicle_id: str, update: VehicleTelemetryUpdate, engine: SimulationEngine = Depends(get_engine)):
    update.vehicle_id = vehicle_id
    success = engine.update_vehicle_target(update)
    if not success:
        raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")
    return {"vehicle_id": vehicle_id, "updated": True}
