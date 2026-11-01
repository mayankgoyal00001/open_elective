"""
SmartV2V Configuration and Constants
Automotive Simulation & Safety Engine Parameters
"""
from pydantic import BaseModel, Field

class SimulationSettings(BaseModel):
    # Time and execution
    time_step: float = Field(default=0.05, description="Simulation physics time step in seconds (20 Hz)")
    speed_multiplier: float = Field(default=1.0, ge=0.1, le=5.0, description="Simulation speed factor")
    
    # Vehicle population
    vehicle_count: int = Field(default=6, ge=2, le=16, description="Number of active simulated vehicles")
    
    # V2V Wireless Communication Layer parameters
    communication_range_m: float = Field(default=200.0, ge=30.0, le=600.0, description="Max wireless communication range in meters")
    message_frequency_hz: float = Field(default=10.0, ge=1.0, le=25.0, description="BSM broadcast rate in Hz (10 Hz is SAE J2735 standard)")
    packet_loss_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Simulated wireless packet loss percentage (0-100%)")
    network_latency_ms: float = Field(default=20.0, ge=0.0, le=500.0, description="Simulated network propagation & queue delay in milliseconds")
    
    # Safety Engine Thresholds (ISO 15623 / SAE J2735 Forward Collision Warning standards)
    ttc_critical_threshold_s: float = Field(default=2.5, description="Time-To-Collision (TTC) critical alert threshold in seconds")
    ttc_warning_threshold_s: float = Field(default=4.5, description="Time-To-Collision (TTC) advisory warning threshold in seconds")
    safe_headway_distance_m: float = Field(default=15.0, description="Safe minimum longitudinal distance in meters")
    emergency_brake_decel_threshold: float = Field(default=-4.5, description="Deceleration rate (m/s^2) that triggers Emergency Electronic Brake Light (EEBL)")
    stale_message_threshold_s: float = Field(default=0.8, description="Age in seconds after which a received V2V message is marked stale")
    
    # Visual map coordinate dimensions
    road_length_m: float = Field(default=600.0, description="Length of horizontal highway road in meters")
    lane_width_m: float = Field(default=4.0, description="Standard road lane width in meters")

settings = SimulationSettings()
