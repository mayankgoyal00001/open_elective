"""
Vehicle State Models for SmartV2V
Represents vehicle telemetry, geometry, kinematics, and dynamic state.
"""
from typing import Optional, List
from pydantic import BaseModel, Field

class VehicleDimensions(BaseModel):
    length_m: float = Field(default=4.8, description="Vehicle length in meters")
    width_m: float = Field(default=2.0, description="Vehicle width in meters")

class VehicleState(BaseModel):
    vehicle_id: str = Field(..., description="Unique vehicle identifier e.g. V2V-01")
    x: float = Field(..., description="X coordinate in meters (longitudinal position)")
    y: float = Field(..., description="Y coordinate in meters (lateral position / lane)")
    speed_kmh: float = Field(default=0.0, description="Vehicle speed in kilometers per hour")
    speed_ms: float = Field(default=0.0, description="Vehicle speed in meters per second")
    target_speed_ms: float = Field(default=25.0, description="Cruising desired speed in m/s")
    heading: float = Field(default=0.0, description="Heading in degrees (0 = East, 90 = North, 180 = West, 270 = South)")
    acceleration: float = Field(default=0.0, description="Longitudinal acceleration in m/s^2")
    braking: bool = Field(default=False, description="Whether mechanical brakes are active")
    emergency_braking: bool = Field(default=False, description="Emergency electronic brake status")
    lane_id: int = Field(default=0, description="Lane index (0 = slow lane, 1 = middle, 2 = fast lane)")
    dimensions: VehicleDimensions = Field(default_factory=VehicleDimensions)
    communication_range: float = Field(default=200.0, description="Wireless V2V communication range in meters")
    risk_level: str = Field(default="SAFE", description="Current evaluated collision risk: SAFE, WARNING, CRITICAL")
    active_warning_reason: Optional[str] = Field(default=None, description="Explanation of active collision alert if any")
    partner_vehicle_id: Optional[str] = Field(default=None, description="Conflicting vehicle ID if warning is active")
    ttc_seconds: Optional[float] = Field(default=None, description="Computed Time to Collision in seconds")
    color: str = Field(default="#3B82F6", description="Display color code")
    driver_profile: str = Field(default="normal", description="Driver behavioral model: normal, cautious, aggressive")
    updated_at: float = Field(default=0.0, description="Simulated timestamp in seconds")

class VehicleTelemetryUpdate(BaseModel):
    vehicle_id: str
    target_speed_kmh: Optional[float] = None
    manual_brake: Optional[bool] = None
    emergency_brake: Optional[bool] = None
    lane_change: Optional[int] = None
