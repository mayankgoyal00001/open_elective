"""
Network and Simulation Analytics Metrics
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class PerVehicleCommMetrics(BaseModel):
    vehicle_id: str
    messages_transmitted: int = 0
    messages_received: int = 0
    messages_dropped: int = 0
    stale_messages_count: int = 0
    neighbors_in_range_count: int = 0
    last_seq_received: Dict[str, int] = Field(default_factory=dict)

class SimulationMetrics(BaseModel):
    simulation_time_seconds: float = 0.0
    active_vehicles: int = 0
    v2v_messages_per_second: float = 0.0
    current_collision_warnings: int = 0
    current_critical_alerts: int = 0
    average_latency_ms: float = 0.0
    packet_delivery_percentage: float = 100.0
    total_messages_sent: int = 0
    total_messages_delivered: int = 0
    total_messages_dropped: int = 0
    stale_telemetry_count: int = 0
    measured_processing_time_ms: float = 0.0
    per_vehicle_metrics: Dict[str, PerVehicleCommMetrics] = Field(default_factory=dict)
