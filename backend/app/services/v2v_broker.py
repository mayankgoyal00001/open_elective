"""
Simulated V2V Wireless Communication Broker
Handles range filtering, transmission delays, packet loss, sequence tracking,
and per-vehicle received message tables without physical radio hardware.
"""
import math
import random
import time
from typing import Dict, List, Optional, Tuple, Deque
from collections import deque
from app.models.vehicle import VehicleState
from app.models.message import V2VMessage, ReceivedMessageRecord, NetworkTransmissionLog
from app.models.metrics import PerVehicleCommMetrics
from app.core.config import SimulationSettings

class V2VCommunicationBroker:
    def __init__(self, settings: SimulationSettings):
        self.settings = settings
        
        # Per-vehicle sequence counters: {vehicle_id: current_sequence_num}
        self.sequence_counters: Dict[str, int] = {}
        
        # In-transit queue: list of (deliver_at_sim_time, receiver_id, message, distance, latency_ms)
        self.transit_queue: List[Tuple[float, str, V2VMessage, float, float]] = []
        
        # Per-vehicle received message store: {receiver_id: {sender_id: ReceivedMessageRecord}}
        self.received_tables: Dict[str, Dict[str, ReceivedMessageRecord]] = {}
        
        # Transmission logs for inspector (rolling buffer of last 200 packets)
        self.transmission_logs: Deque[NetworkTransmissionLog] = deque(maxlen=200)
        
        # Performance counters
        self.total_messages_sent: int = 0
        self.total_messages_delivered: int = 0
        self.total_messages_dropped_loss: int = 0
        self.total_messages_out_of_range: int = 0
        
        # Latency tracking (last 100 delivered packets)
        self.recent_latencies: Deque[float] = deque(maxlen=100)
        
        # Throughput tracking: timestamps of deliveries in the last 1.0 second
        self.delivery_timestamps: Deque[float] = deque()
        
        # Per-vehicle metrics
        self.per_vehicle_metrics: Dict[str, PerVehicleCommMetrics] = {}
        
        # Range tracking: remember who was in range of whom to generate enter/exit events
        self.neighbors_in_range: Dict[str, set] = {}

    def reset(self):
        self.sequence_counters.clear()
        self.transit_queue.clear()
        self.received_tables.clear()
        self.transmission_logs.clear()
        self.total_messages_sent = 0
        self.total_messages_delivered = 0
        self.total_messages_dropped_loss = 0
        self.total_messages_out_of_range = 0
        self.recent_latencies.clear()
        self.delivery_timestamps.clear()
        self.per_vehicle_metrics.clear()
        self.neighbors_in_range.clear()

    def get_next_sequence_number(self, vehicle_id: str) -> int:
        seq = self.sequence_counters.get(vehicle_id, 0) + 1
        self.sequence_counters[vehicle_id] = seq
        return seq

    def _ensure_vehicle_metrics(self, vehicle_id: str):
        if vehicle_id not in self.per_vehicle_metrics:
            self.per_vehicle_metrics[vehicle_id] = PerVehicleCommMetrics(vehicle_id=vehicle_id)
        if vehicle_id not in self.received_tables:
            self.received_tables[vehicle_id] = {}
        if vehicle_id not in self.neighbors_in_range:
            self.neighbors_in_range[vehicle_id] = set()

    def broadcast_message(
        self,
        sender: VehicleState,
        all_vehicles: List[VehicleState],
        sim_time: float
    ) -> Tuple[V2VMessage, List[str]]:
        """
        Broadcasts a Basic Safety Message (BSM) from sender to all eligible vehicles within range.
        Returns the generated message and list of range-enter/exit event descriptions.
        """
        self._ensure_vehicle_metrics(sender.vehicle_id)
        seq = self.get_next_sequence_number(sender.vehicle_id)
        
        event_flags = []
        if sender.emergency_braking:
            event_flags.append("EMERGENCY_BRAKE_ACTIVE")
        elif sender.braking:
            event_flags.append("BRAKE_ACTIVE")
        if sender.acceleration < -4.0:
            event_flags.append("HARD_DECELERATION")

        msg = V2VMessage(
            message_id=f"MSG-{sender.vehicle_id}-{seq}",
            sender_id=sender.vehicle_id,
            sequence_number=seq,
            timestamp=sim_time,
            position_x=round(sender.x, 2),
            position_y=round(sender.y, 2),
            speed_kmh=round(sender.speed_kmh, 1),
            speed_ms=round(sender.speed_ms, 2),
            heading=round(sender.heading, 1),
            acceleration=round(sender.acceleration, 2),
            brake_active=sender.braking,
            emergency_brake_active=sender.emergency_braking,
            lane_id=sender.lane_id,
            event_flags=event_flags
        )

        self.per_vehicle_metrics[sender.vehicle_id].messages_transmitted += 1
        self.total_messages_sent += 1

        range_events = []
        current_in_range = set()

        # Deliver to all other simulated vehicles
        for receiver in all_vehicles:
            if receiver.vehicle_id == sender.vehicle_id:
                continue
                
            self._ensure_vehicle_metrics(receiver.vehicle_id)
            
            # Calculate Euclidean distance
            dx = sender.x - receiver.x
            dy = sender.y - receiver.y
            dist = math.hypot(dx, dy)
            
            # Check communication range
            comm_range = min(sender.communication_range, self.settings.communication_range_m)
            
            if dist <= comm_range:
                current_in_range.add(receiver.vehicle_id)
                # Check if newly in range
                if receiver.vehicle_id not in self.neighbors_in_range[sender.vehicle_id]:
                    range_events.append(f"{receiver.vehicle_id} entered V2V range of {sender.vehicle_id} ({dist:.1f}m)")

                # Check packet loss simulation
                loss_chance = self.settings.packet_loss_percent / 100.0
                if random.random() < loss_chance:
                    # Message dropped due to RF interference / packet loss
                    self.total_messages_dropped_loss += 1
                    self.per_vehicle_metrics[receiver.vehicle_id].messages_dropped += 1
                    self.transmission_logs.append(NetworkTransmissionLog(
                        packet_id=msg.message_id,
                        sender_id=sender.vehicle_id,
                        target_id=receiver.vehicle_id,
                        sent_at=sim_time,
                        status="DROPPED_PACKET_LOSS",
                        latency_ms=0.0,
                        distance_m=round(dist, 1)
                    ))
                else:
                    # Successful delivery scheduled with network latency + slight jitter (+/- 10%)
                    jitter_factor = random.uniform(0.9, 1.1)
                    actual_latency_ms = max(1.0, self.settings.network_latency_ms * jitter_factor)
                    deliver_time = sim_time + (actual_latency_ms / 1000.0)
                    
                    self.transit_queue.append((
                        deliver_time,
                        receiver.vehicle_id,
                        msg,
                        dist,
                        actual_latency_ms
                    ))
            else:
                # Out of range
                if receiver.vehicle_id in self.neighbors_in_range[sender.vehicle_id]:
                    range_events.append(f"{receiver.vehicle_id} left V2V range of {sender.vehicle_id} ({dist:.1f}m)")
                self.total_messages_out_of_range += 1

        self.neighbors_in_range[sender.vehicle_id] = current_in_range
        self.per_vehicle_metrics[sender.vehicle_id].neighbors_in_range_count = len(current_in_range)
        
        return msg, range_events

    def process_transit_queue(self, current_sim_time: float):
        """
        Processes packets in the transit queue that have reached their delivery time.
        """
        remaining_queue = []
        for deliver_time, receiver_id, msg, dist, latency_ms in self.transit_queue:
            if deliver_time <= current_sim_time:
                # Deliver to receiver table
                self._ensure_vehicle_metrics(receiver_id)
                
                # Check sequence gap
                last_seq = self.per_vehicle_metrics[receiver_id].last_seq_received.get(msg.sender_id, 0)
                self.per_vehicle_metrics[receiver_id].last_seq_received[msg.sender_id] = msg.sequence_number
                
                rec = ReceivedMessageRecord(
                    message=msg,
                    received_at=current_sim_time,
                    latency_ms=round(latency_ms, 1),
                    distance_at_reception_m=round(dist, 1),
                    is_stale=False
                )
                self.received_tables[receiver_id][msg.sender_id] = rec
                
                # Update metrics
                self.total_messages_delivered += 1
                self.per_vehicle_metrics[receiver_id].messages_received += 1
                self.recent_latencies.append(latency_ms)
                self.delivery_timestamps.append(current_sim_time)
                
                self.transmission_logs.append(NetworkTransmissionLog(
                    packet_id=msg.message_id,
                    sender_id=msg.sender_id,
                    target_id=receiver_id,
                    sent_at=msg.timestamp,
                    delivered_at=current_sim_time,
                    status="DELIVERED",
                    latency_ms=round(latency_ms, 1),
                    distance_m=round(dist, 1)
                ))
            else:
                remaining_queue.append((deliver_time, receiver_id, msg, dist, latency_ms))
        
        self.transit_queue = remaining_queue

    def update_freshness(self, current_sim_time: float):
        """
        Checks freshness of received messages and marks stale messages.
        """
        stale_threshold = self.settings.stale_message_threshold_s
        for receiver_id, sender_map in self.received_tables.items():
            stale_count = 0
            for sender_id, rec in sender_map.items():
                age = current_sim_time - rec.message.timestamp
                if age > stale_threshold:
                    rec.is_stale = True
                    stale_count += 1
                else:
                    rec.is_stale = False
            if receiver_id in self.per_vehicle_metrics:
                self.per_vehicle_metrics[receiver_id].stale_messages_count = stale_count

    def get_delivery_ratio(self) -> float:
        total_attempts = self.total_messages_delivered + self.total_messages_dropped_loss
        if total_attempts == 0:
            return 100.0
        return round((self.total_messages_delivered / total_attempts) * 100.0, 1)

    def get_average_latency_ms(self) -> float:
        if not self.recent_latencies:
            return self.settings.network_latency_ms
        return round(sum(self.recent_latencies) / len(self.recent_latencies), 1)

    def get_current_message_rate_hz(self, current_sim_time: float) -> float:
        # Prune delivery timestamps older than 1.0 second
        while self.delivery_timestamps and (current_sim_time - self.delivery_timestamps[0] > 1.0):
            self.delivery_timestamps.popleft()
        return float(len(self.delivery_timestamps))

    def get_total_stale_count(self) -> int:
        count = 0
        for receiver_id, sender_map in self.received_tables.items():
            for sender_id, rec in sender_map.items():
                if rec.is_stale:
                    count += 1
        return count
