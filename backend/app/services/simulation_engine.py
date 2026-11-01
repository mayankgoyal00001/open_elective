"""
Authoritative Vehicle Simulation Engine
Runs kinematics integration, car-following behaviors, V2V communication cycles,
and collision safety evaluations at a fixed authoritative timestep.
"""
import asyncio
import math
import time
from collections import deque
from typing import List, Dict, Optional, Tuple, Deque, Callable
from app.models.vehicle import VehicleState, VehicleTelemetryUpdate
from app.models.event import SafetyEvent
from app.models.metrics import SimulationMetrics
from app.core.config import SimulationSettings, settings as global_settings
from app.services.v2v_broker import V2VCommunicationBroker
from app.services.safety_engine import SafetyEngine
from app.services.scenario_manager import ScenarioManager

class SimulationEngine:
    def __init__(self, settings: Optional[SimulationSettings] = None):
        self.settings = settings or global_settings
        self.v2v_broker = V2VCommunicationBroker(self.settings)
        self.safety_engine = SafetyEngine(self.settings)
        
        # Simulation state
        self.status: str = "STOPPED"  # STOPPED, RUNNING, PAUSED
        self.sim_time: float = 0.0
        self.active_scenario_id: str = "normal_traffic"
        self.is_intersection: bool = False
        
        self.vehicles: List[VehicleState] = []
        self.recent_events: Deque[SafetyEvent] = deque(maxlen=200)
        
        # Timing
        self.last_broadcast_sim_time: float = 0.0
        self._loop_task: Optional[asyncio.Task] = None
        self._listeners: List[Callable[[], None]] = []
        
        # Measured execution time
        self.measured_tick_ms: float = 0.0
        
        # Initialize default scenario
        self.load_scenario("normal_traffic")

    def register_listener(self, callback: Callable[[], None]):
        self._listeners.append(callback)

    def notify_listeners(self):
        for listener in self._listeners:
            try:
                listener()
            except Exception:
                pass

    def load_scenario(self, scenario_id: str):
        self.active_scenario_id = scenario_id
        self.sim_time = 0.0
        self.last_broadcast_sim_time = 0.0
        self.v2v_broker.reset()
        self.safety_engine.reset()
        self.recent_events.clear()
        
        vehicles, is_int = ScenarioManager.setup_scenario(scenario_id, self.settings)
        self.vehicles = vehicles
        self.is_intersection = is_int
        
        self.recent_events.append(SafetyEvent(
            event_id="EVT-00000",
            timestamp=0.0,
            event_type="SCENARIO_START",
            severity="INFO",
            primary_vehicle_id="SYSTEM",
            description=f"Loaded scenario: {scenario_id.replace('_', ' ').title()}"
        ))

    def reset(self):
        self.load_scenario(self.active_scenario_id)

    async def start(self):
        if self.status == "RUNNING":
            return
        self.status = "RUNNING"
        if self._loop_task is None or self._loop_task.done():
            self._loop_task = asyncio.create_task(self._simulation_loop())

    async def pause(self):
        self.status = "PAUSED"

    async def resume(self):
        if self.status == "PAUSED":
            self.status = "RUNNING"
        elif self.status == "STOPPED":
            await self.start()

    async def stop(self):
        self.status = "STOPPED"
        if self._loop_task and not self._loop_task.done():
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
        self._loop_task = None

    def trigger_emergency_brake(self, vehicle_id: str):
        """
        Manually trigger emergency electronic braking on a specific vehicle.
        Simulates sudden driver intervention or road hazard detection.
        """
        for v in self.vehicles:
            if v.vehicle_id == vehicle_id:
                v.braking = True
                v.emergency_braking = True
                v.acceleration = -8.5
                v.target_speed_ms = 0.0
                
                self.recent_events.append(SafetyEvent(
                    event_id=self.safety_engine._generate_event_id(),
                    timestamp=self.sim_time,
                    event_type="EMERGENCY_BRAKE",
                    severity="CRITICAL",
                    primary_vehicle_id=vehicle_id,
                    description=f"Manual Emergency Brake triggered on vehicle {vehicle_id} (-8.5 m/s²)"
                ))
                return True
        return False

    def update_vehicle_target(self, update: VehicleTelemetryUpdate):
        for v in self.vehicles:
            if v.vehicle_id == update.vehicle_id:
                if update.target_speed_kmh is not None:
                    v.target_speed_ms = max(0.0, update.target_speed_kmh / 3.6)
                if update.manual_brake is not None:
                    v.braking = update.manual_brake
                    if update.manual_brake:
                        v.acceleration = -3.5
                if update.emergency_brake is not None:
                    v.emergency_braking = update.emergency_brake
                    v.braking = update.emergency_brake
                    if update.emergency_brake:
                        v.acceleration = -8.5
                return True
        return False

    def _step_kinematics(self, dt: float):
        """
        Authoritative numerical integration of vehicle kinematics.
        Units:
        - Position: meters (m)
        - Speed: m/s (converted to km/h for telemetry display)
        - Acceleration: m/s^2
        """
        road_wrap_length = self.settings.road_length_m

        for v in self.vehicles:
            # 1. Update acceleration based on target speed and braking
            if v.emergency_braking:
                v.acceleration = -8.5
            elif v.braking:
                v.acceleration = -3.5
            else:
                # Car-following / target speed regulation
                speed_diff = v.target_speed_ms - v.speed_ms
                if abs(speed_diff) < 0.2:
                    v.acceleration = 0.0
                elif speed_diff > 0:
                    v.acceleration = min(2.5, speed_diff * 0.8)  # Smooth acceleration
                else:
                    v.acceleration = max(-3.0, speed_diff * 1.2)  # Normal deceleration

            # In scenarios other than rear_end_risk or emergency_braking,
            # apply gentle collision-avoidance car-following (Intelligent Driver Model principle)
            if self.active_scenario_id == "normal_traffic" and not self.is_intersection:
                leaders = [
                    l for l in self.vehicles 
                    if l.vehicle_id != v.vehicle_id 
                    and l.lane_id == v.lane_id 
                    and l.x > v.x
                ]
                if leaders:
                    lead = min(leaders, key=lambda l: l.x - v.x)
                    gap = lead.x - v.x - v.dimensions.length_m
                    desired_gap = max(12.0, v.speed_ms * 1.5)
                    if gap < desired_gap:
                        # Decelerate to match leader
                        v.acceleration = min(v.acceleration, -2.5 * (1.0 - (gap / desired_gap)))

            # 2. Integrate speed: v_new = max(0, v + a * dt)
            new_speed = max(0.0, v.speed_ms + v.acceleration * dt)
            
            # If vehicle came to complete stop under emergency brake, stop braking acceleration
            if new_speed == 0.0 and v.acceleration < 0:
                v.acceleration = 0.0
                
            v.speed_ms = round(new_speed, 2)
            v.speed_kmh = round(new_speed * 3.6, 1)

            # 3. Integrate position based on heading
            rad = math.radians(v.heading)
            dx = v.speed_ms * math.cos(rad) * dt
            dy = v.speed_ms * math.sin(rad) * dt
            
            v.x += dx
            v.y += dy
            v.updated_at = self.sim_time

            # 4. Handle boundary condition (highway wrap-around)
            if not self.is_intersection:
                if v.x > road_wrap_length:
                    v.x = 0.0  # Smooth loop-back to highway start
                elif v.x < 0.0:
                    v.x = road_wrap_length

    def step(self):
        """
        Executes a single discrete simulation tick.
        """
        start_exec = time.perf_counter()
        
        # Compute effective dt adjusted by speed multiplier
        dt = self.settings.time_step * self.settings.speed_multiplier
        self.sim_time = round(self.sim_time + dt, 3)

        # 1. Authoritative vehicle physics
        self._step_kinematics(dt)

        # 2. Periodic V2V Basic Safety Message (BSM) Broadcast
        broadcast_period = 1.0 / max(1.0, self.settings.message_frequency_hz)
        if (self.sim_time - self.last_broadcast_sim_time) >= broadcast_period:
            for sender in self.vehicles:
                _, range_events = self.v2v_broker.broadcast_message(
                    sender, self.vehicles, self.sim_time
                )
                for r_desc in range_events:
                    self.recent_events.append(SafetyEvent(
                        event_id=self.safety_engine._generate_event_id(),
                        timestamp=self.sim_time,
                        event_type="RANGE_CHANGE",
                        severity="INFO",
                        primary_vehicle_id=sender.vehicle_id,
                        description=r_desc
                    ))
            self.last_broadcast_sim_time = self.sim_time

        # 3. Process in-transit network queue (simulated latency delivery)
        self.v2v_broker.process_transit_queue(self.sim_time)

        # 4. Update message freshness and stale detection
        self.v2v_broker.update_freshness(self.sim_time)

        # 5. Collision Detection & Safety Evaluation
        self.vehicles, safety_events = self.safety_engine.evaluate_safety(
            self.vehicles,
            self.v2v_broker.received_tables,
            self.sim_time,
            is_intersection_scenario=self.is_intersection
        )
        for evt in safety_events:
            self.recent_events.append(evt)

        # Record measured execution performance
        self.measured_tick_ms = round((time.perf_counter() - start_exec) * 1000.0, 2)
        self.notify_listeners()

    async def _simulation_loop(self):
        while self.status == "RUNNING":
            tick_start = time.perf_counter()
            self.step()
            
            # Sleep remainder of time step
            elapsed = time.perf_counter() - tick_start
            sleep_duration = max(0.005, self.settings.time_step - elapsed)
            await asyncio.sleep(sleep_duration)

    def get_metrics(self) -> SimulationMetrics:
        active_warnings = sum(1 for v in self.vehicles if v.risk_level == "WARNING")
        active_critical = sum(1 for v in self.vehicles if v.risk_level == "CRITICAL")
        
        return SimulationMetrics(
            simulation_time_seconds=round(self.sim_time, 2),
            active_vehicles=len(self.vehicles),
            v2v_messages_per_second=self.v2v_broker.get_current_message_rate_hz(self.sim_time),
            current_collision_warnings=active_warnings,
            current_critical_alerts=active_critical,
            average_latency_ms=self.v2v_broker.get_average_latency_ms(),
            packet_delivery_percentage=self.v2v_broker.get_delivery_ratio(),
            total_messages_sent=self.v2v_broker.total_messages_sent,
            total_messages_delivered=self.v2v_broker.total_messages_delivered,
            total_messages_dropped=self.v2v_broker.total_messages_dropped_loss,
            stale_telemetry_count=self.v2v_broker.get_total_stale_count(),
            measured_processing_time_ms=self.measured_tick_ms,
            per_vehicle_metrics=self.v2v_broker.per_vehicle_metrics
        )

    def get_full_state_snapshot(self) -> Dict:
        return {
            "status": self.status,
            "sim_time": round(self.sim_time, 2),
            "scenario_id": self.active_scenario_id,
            "is_intersection": self.is_intersection,
            "vehicles": [v.model_dump() for v in self.vehicles],
            "metrics": self.get_metrics().model_dump(),
            "recent_events": [e.model_dump() for e in list(self.recent_events)[-35:]],
            "settings": self.settings.model_dump()
        }
