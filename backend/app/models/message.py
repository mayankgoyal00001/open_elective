"""
V2V Cooperative Message Specification
Modeled after SAE J2735 Basic Safety Message (BSM) & ETSI CAM
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class V2VMessage(BaseModel):
    message_id: str = Field(..., description="Unique message packet ID")
    sender_id: str = Field(..., description="Transmitting vehicle ID")
    sequence_number: int = Field(..., description="Monotonically increasing sequence number per vehicle")
    timestamp: float = Field(..., description="Simulated timestamp when message was broadcast (seconds)")
    
    # Kinematic payload
    position_x: float = Field(..., description="Longitudinal position in meters")
    position_y: float = Field(..., description="Lateral position in meters")
    speed_kmh: float = Field(..., description="Speed in km/h")
    speed_ms: float = Field(..., description="Speed in m/s")
    heading: float = Field(..., description="Vehicle heading in degrees")
    acceleration: float = Field(..., description="Longitudinal acceleration in m/s^2")
    
    # Safety indicator flags
    brake_active: bool = Field(default=False, description="Primary brake engaged")
    emergency_brake_active: bool = Field(default=False, description="Emergency Electronic Brake Light active")
    lane_id: int = Field(default=0, description="Current road lane index")
    event_flags: List[str] = Field(default_factory=list, description="Automotive event flags (e.g. EEBL, FCW_ALERT)")

class ReceivedMessageRecord(BaseModel):
    message: V2VMessage
    received_at: float = Field(..., description="Timestamp when message arrived at receiver (seconds)")
    latency_ms: float = Field(..., description="Simulated network transmission latency in milliseconds")
    distance_at_reception_m: float = Field(..., description="Distance between transmitter and receiver")
    is_stale: bool = Field(default=False, description="Whether message freshness has expired")

class NetworkTransmissionLog(BaseModel):
    packet_id: str
    sender_id: str
    target_id: str
    sent_at: float
    delivered_at: Optional[float] = None
    status: str = Field(..., description="DELIVERED, DROPPED_OUT_OF_RANGE, DROPPED_PACKET_LOSS, IN_TRANSIT")
    latency_ms: float = Field(default=0.0)
    distance_m: float = Field(default=0.0)
