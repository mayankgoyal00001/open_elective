"""
Automotive Collision Detection and Safety Engine
Implements Time to Collision (TTC), Forward Collision Warning (FCW),
Electronic Emergency Brake Light (EEBL), and Intersection Conflict Warning (ICW)
with stateful hysteresis to prevent alert flickering.
"""
import math
from typing import Dict, List, Optional, Tuple, Set
from app.models.vehicle import VehicleState
from app.models.message import ReceivedMessageRecord
from app.models.event import SafetyEvent
from app.core.config import SimulationSettings

class RiskStateDebouncer:
    """
    Prevents alert flickering by requiring consecutive cycles to confirm state transitions.
    """
    def __init__(self, escalate_cycles: int = 2, deescalate_cycles: int = 3):
        self.escalate_cycles = escalate_cycles
        self.deescalate_cycles = deescalate_cycles
        # {pair_key: {"current": "SAFE", "candidate": "WARNING", "count": 1}}
        self.pair_states: Dict[str, Dict] = {}

    def get_state(self, pair_key: str) -> str:
        if pair_key not in self.pair_states:
            return "SAFE"
        return self.pair_states[pair_key]["current"]

    def update(self, pair_key: str, detected_level: str) -> str:
        if pair_key not in self.pair_states:
            if detected_level == "SAFE":
                self.pair_states[pair_key] = {
                    "current": "SAFE",
                    "candidate": "SAFE",
                    "count": 0
                }
                return "SAFE"
            else:
                # First time seeing a warning/critical condition: require confirmation
                self.pair_states[pair_key] = {
                    "current": "SAFE",
                    "candidate": detected_level,
                    "count": 1
                }
                return "SAFE"

        entry = self.pair_states[pair_key]
        current = entry["current"]

        if detected_level == current:
            entry["candidate"] = current
            entry["count"] = 0
            return current

        # Severity rank
        severity_rank = {"SAFE": 0, "WARNING": 1, "CRITICAL": 2}
        is_escalation = severity_rank.get(detected_level, 0) > severity_rank.get(current, 0)
        required_cycles = self.escalate_cycles if is_escalation else self.deescalate_cycles

        if entry["candidate"] == detected_level:
            entry["count"] += 1
            if entry["count"] >= required_cycles:
                entry["current"] = detected_level
                entry["count"] = 0
                return detected_level
        else:
            entry["candidate"] = detected_level
            entry["count"] = 1

        return current

    def reset(self):
        self.pair_states.clear()


class SafetyEngine:
    def __init__(self, settings: SimulationSettings):
        self.settings = settings
        self.debouncer = RiskStateDebouncer(escalate_cycles=2, deescalate_cycles=3)
        self.active_events: List[SafetyEvent] = []
        self.event_counter: int = 0

    def reset(self):
        self.debouncer.reset()
        self.active_events.clear()
        self.event_counter = 0

    def _generate_event_id(self) -> str:
        self.event_counter += 1
        return f"EVT-{self.event_counter:05d}"

    def compute_ttc_same_lane(
        self,
        follower_x: float,
        follower_speed_ms: float,
        leader_x: float,
        leader_speed_ms: float,
        vehicle_length: float = 4.8
    ) -> Optional[float]:
        """
        Calculates Time To Collision for vehicles in the same lane.
        TTC = Net Clearance / Closing Speed
        """
        # Follower must be behind leader along longitudinal axis
        clearance = leader_x - follower_x - vehicle_length
        if clearance <= 0:
            # Overlap or collision point
            return 0.0

        closing_speed = follower_speed_ms - leader_speed_ms
        if closing_speed > 0.1:  # Follower closing in on leader
            ttc = clearance / closing_speed
            return round(ttc, 2)
        
        # Vehicles diverging or maintaining exact speed: no collision predicted
        return None

    def evaluate_intersection_conflict(
        self,
        v_ew: VehicleState,
        v_ns: VehicleState,
        intersection_center: Tuple[float, float] = (300.0, 50.0),
        conflict_radius: float = 18.0
    ) -> Optional[Tuple[str, float, float]]:
        """
        Evaluates crossing conflict for perpendicular paths (East-West vs North-South).
        Returns (risk_level, time_difference, min_distance_to_center) if conflict detected.
        """
        cx, cy = intersection_center
        
        # East-West vehicle: distance to intersection along x
        # If heading ~ 0 (moving East): distance = cx - v_ew.x
        dist_ew = cx - v_ew.x
        speed_ew = max(0.5, v_ew.speed_ms)
        time_ew_enter = (dist_ew - conflict_radius) / speed_ew
        time_ew_exit = (dist_ew + conflict_radius) / speed_ew

        # North-South vehicle: distance to intersection along y
        # If heading ~ 90 (moving North): distance = cy - v_ns.y
        dist_ns = cy - v_ns.y
        speed_ns = max(0.5, v_ns.speed_ms)
        time_ns_enter = (dist_ns - conflict_radius) / speed_ns
        time_ns_exit = (dist_ns + conflict_radius) / speed_ns

        # Both must be approaching (not already past)
        if time_ew_exit < 0 or time_ns_exit < 0:
            return None
            
        if dist_ew < -conflict_radius or dist_ns < -conflict_radius:
            return None

        # Check time overlap in conflict zone
        overlap_start = max(time_ew_enter, time_ns_enter)
        overlap_end = min(time_ew_exit, time_ns_exit)

        if overlap_start <= overlap_end:
            time_diff = abs(time_ew_enter - time_ns_enter)
            dist_center = math.hypot(v_ew.x - cx, v_ew.y - cy)
            
            # Level based on how close time overlap is
            if time_diff < 1.2 and (dist_ew <= 70 and dist_ns <= 70):
                return ("CRITICAL", time_diff, dist_center)
            elif time_diff < 2.8 and (dist_ew <= 140 and dist_ns <= 140):
                return ("WARNING", time_diff, dist_center)

        return None

    def evaluate_safety(
        self,
        vehicles: List[VehicleState],
        received_tables: Dict[str, Dict[str, ReceivedMessageRecord]],
        sim_time: float,
        is_intersection_scenario: bool = False
    ) -> Tuple[List[VehicleState], List[SafetyEvent]]:
        """
        Primary evaluation loop. Evaluates safety based on authoritative vehicle telemetry
        AND received V2V cooperative messages, respecting communication realism.
        """
        new_events: List[SafetyEvent] = []
        vehicles_dict = {v.vehicle_id: v for v in vehicles}
        
        # Reset per-tick dynamic risk state for evaluation
        for v in vehicles:
            v.risk_level = "SAFE"
            v.active_warning_reason = None
            v.partner_vehicle_id = None
            v.ttc_seconds = None

        # Check 1: Electronic Emergency Brake Light (EEBL)
        # Any vehicle braking aggressively broadcasts EEBL to neighbors in range
        for v in vehicles:
            if v.emergency_braking or v.acceleration <= self.settings.emergency_brake_decel_threshold:
                # Check which vehicles received this via V2V
                for other_id, rec_table in received_tables.items():
                    if other_id == v.vehicle_id or other_id not in vehicles_dict:
                        continue
                    if v.vehicle_id in rec_table:
                        rec = rec_table[v.vehicle_id]
                        if not rec.is_stale and rec.message.emergency_brake_active:
                            other_v = vehicles_dict[other_id]
                            # If follower is in same lane and behind the emergency braking vehicle
                            if other_v.lane_id == v.lane_id and other_v.x < v.x and (v.x - other_v.x) < 180.0:
                                pair_key = f"{other_id}->{v.vehicle_id}:EEBL"
                                debounced_level = self.debouncer.update(pair_key, "CRITICAL")
                                
                                other_v.risk_level = debounced_level
                                other_v.active_warning_reason = f"V2V EEBL: Lead vehicle {v.vehicle_id} emergency braking!"
                                other_v.partner_vehicle_id = v.vehicle_id
                                
                                # Compute instantaneous TTC
                                ttc = self.compute_ttc_same_lane(other_v.x, other_v.speed_ms, v.x, v.speed_ms)
                                other_v.ttc_seconds = ttc
                                
                                new_events.append(SafetyEvent(
                                    event_id=self._generate_event_id(),
                                    timestamp=sim_time,
                                    event_type="EMERGENCY_BRAKE",
                                    severity="CRITICAL",
                                    primary_vehicle_id=other_id,
                                    secondary_vehicle_id=v.vehicle_id,
                                    description=f"Emergency Brake Warning (EEBL): {v.vehicle_id} braking hard ahead ({rec.distance_at_reception_m}m)",
                                    ttc_seconds=ttc,
                                    distance_m=round(v.x - other_v.x, 1)
                                ))

        # Check 2: Same-Lane Forward Collision Warning (FCW) & Time To Collision (TTC)
        for i, follower in enumerate(vehicles):
            # Only evaluate against vehicles ahead in the same lane
            leaders = [
                v for v in vehicles 
                if v.vehicle_id != follower.vehicle_id 
                and v.lane_id == follower.lane_id 
                and v.x > follower.x
            ]
            
            if not leaders:
                continue
                
            # Nearest leader in same lane
            nearest_leader = min(leaders, key=lambda l: l.x - follower.x)
            dist_longitudinal = nearest_leader.x - follower.x
            net_clearance = dist_longitudinal - follower.dimensions.length_m
            
            ttc = self.compute_ttc_same_lane(
                follower.x, follower.speed_ms,
                nearest_leader.x, nearest_leader.speed_ms,
                follower.dimensions.length_m
            )
            
            pair_key = f"{follower.vehicle_id}->{nearest_leader.vehicle_id}:FCW"
            detected_level = "SAFE"
            reason = None

            # Check if follower has received V2V messages from nearest leader
            has_fresh_v2v = False
            if follower.vehicle_id in received_tables and nearest_leader.vehicle_id in received_tables[follower.vehicle_id]:
                rec = received_tables[follower.vehicle_id][nearest_leader.vehicle_id]
                has_fresh_v2v = not rec.is_stale

            if ttc is not None:
                if ttc < self.settings.ttc_critical_threshold_s:
                    detected_level = "CRITICAL"
                    reason = f"CRITICAL FCW: Closing rapidly on {nearest_leader.vehicle_id} (TTC: {ttc}s, Dist: {net_clearance:.1f}m)"
                elif ttc < self.settings.ttc_warning_threshold_s:
                    detected_level = "WARNING"
                    reason = f"Forward Collision Warning: Approaching {nearest_leader.vehicle_id} (TTC: {ttc}s, Dist: {net_clearance:.1f}m)"
            elif net_clearance < self.settings.safe_headway_distance_m and follower.speed_ms > 2.0:
                detected_level = "WARNING"
                reason = f"Unsafe Headway Distance to {nearest_leader.vehicle_id} ({net_clearance:.1f}m < {self.settings.safe_headway_distance_m}m)"

            if not has_fresh_v2v and detected_level != "SAFE":
                reason += " [V2V Link Degraded / Stale]"

            debounced_level = self.debouncer.update(pair_key, detected_level)
            
            # Apply to vehicle if more severe than existing risk
            severity_rank = {"SAFE": 0, "WARNING": 1, "CRITICAL": 2}
            if severity_rank.get(debounced_level, 0) > severity_rank.get(follower.risk_level, 0):
                follower.risk_level = debounced_level
                follower.active_warning_reason = reason
                follower.partner_vehicle_id = nearest_leader.vehicle_id
                follower.ttc_seconds = ttc
                
                if debounced_level in ["WARNING", "CRITICAL"]:
                    new_events.append(SafetyEvent(
                        event_id=self._generate_event_id(),
                        timestamp=sim_time,
                        event_type="FORWARD_COLLISION",
                        severity=debounced_level,
                        primary_vehicle_id=follower.vehicle_id,
                        secondary_vehicle_id=nearest_leader.vehicle_id,
                        description=reason or "Collision Hazard Detected",
                        ttc_seconds=ttc,
                        distance_m=round(net_clearance, 1)
                    ))

        # Check 3: Intersection Conflict Warning (ICW) if intersection scenario
        if is_intersection_scenario:
            ew_vehicles = [v for v in vehicles if abs(v.heading - 0.0) < 30.0 or abs(v.heading - 180.0) < 30.0]
            ns_vehicles = [v for v in vehicles if abs(v.heading - 90.0) < 30.0 or abs(v.heading - 270.0) < 30.0]

            for v_ew in ew_vehicles:
                for v_ns in ns_vehicles:
                    conflict = self.evaluate_intersection_conflict(v_ew, v_ns)
                    if conflict:
                        risk, time_diff, dist = conflict
                        pair_key = f"INT:{v_ew.vehicle_id}<->{v_ns.vehicle_id}"
                        debounced_level = self.debouncer.update(pair_key, risk)
                        
                        desc = f"Intersection Conflict: Simultaneous arrival at conflict zone (Δt={time_diff:.1f}s)"
                        for v in [v_ew, v_ns]:
                            if severity_rank.get(debounced_level, 0) > severity_rank.get(v.risk_level, 0):
                                v.risk_level = debounced_level
                                v.active_warning_reason = desc
                                v.partner_vehicle_id = v_ns.vehicle_id if v == v_ew else v_ew.vehicle_id
                        
                        if debounced_level in ["WARNING", "CRITICAL"]:
                            new_events.append(SafetyEvent(
                                event_id=self._generate_event_id(),
                                timestamp=sim_time,
                                event_type="INTERSECTION_CONFLICT",
                                severity=debounced_level,
                                primary_vehicle_id=v_ew.vehicle_id,
                                secondary_vehicle_id=v_ns.vehicle_id,
                                description=desc,
                                ttc_seconds=round(time_diff, 2),
                                distance_m=round(dist, 1)
                            ))

        return vehicles, new_events
