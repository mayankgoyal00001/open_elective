"""
Safety and System Event Models for SmartV2V
"""
from typing import Optional, List
from pydantic import BaseModel, Field

class SafetyEvent(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    timestamp: float = Field(..., description="Simulation time in seconds when event occurred")
    event_type: str = Field(..., description="EMERGENCY_BRAKE, FORWARD_COLLISION, INTERSECTION_CONFLICT, RANGE_ENTER, RANGE_EXIT, PACKET_LOSS, SCENARIO_START")
    severity: str = Field(..., description="INFO, WARNING, CRITICAL")
    primary_vehicle_id: str = Field(..., description="Subject vehicle ID")
    secondary_vehicle_id: Optional[str] = Field(default=None, description="Conflicting or partner vehicle ID")
    description: str = Field(..., description="Human-readable event explanation")
    ttc_seconds: Optional[float] = Field(default=None, description="Time to Collision in seconds if applicable")
    distance_m: Optional[float] = Field(default=None, description="Separation distance in meters if applicable")
