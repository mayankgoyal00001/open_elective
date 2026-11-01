"""
Unit Tests for Simulated V2V Communication Broker
Tests range filtering, latency queue, packet loss, sequence numbers, and freshness.
"""
import pytest
from app.models.vehicle import VehicleState
from app.core.config import SimulationSettings
from app.services.v2v_broker import V2VCommunicationBroker

def test_communication_range_filtering():
    settings = SimulationSettings(communication_range_m=100.0, packet_loss_percent=0.0, network_latency_ms=10.0)
    broker = V2VCommunicationBroker(settings)
    
    sender = VehicleState(vehicle_id="V-SEND", x=100.0, y=20.0, speed_ms=20.0)
    in_range_receiver = VehicleState(vehicle_id="V-RECV-NEAR", x=150.0, y=20.0, speed_ms=20.0)   # 50m away
    out_of_range_receiver = VehicleState(vehicle_id="V-RECV-FAR", x=300.0, y=20.0, speed_ms=20.0) # 200m away
    
    all_vehicles = [sender, in_range_receiver, out_of_range_receiver]
    
    msg, range_events = broker.broadcast_message(sender, all_vehicles, sim_time=1.0)
    
    assert msg.sender_id == "V-SEND"
    assert broker.total_messages_sent == 1
    # Only 1 vehicle was in range, so 1 packet should be scheduled in transit queue
    assert len(broker.transit_queue) == 1
    assert broker.transit_queue[0][1] == "V-RECV-NEAR"
    assert broker.total_messages_out_of_range == 1

def test_simulated_network_latency_delivery():
    settings = SimulationSettings(communication_range_m=200.0, packet_loss_percent=0.0, network_latency_ms=50.0)
    broker = V2VCommunicationBroker(settings)
    
    v1 = VehicleState(vehicle_id="V-1", x=50.0, y=20.0, speed_ms=20.0)
    v2 = VehicleState(vehicle_id="V-2", x=100.0, y=20.0, speed_ms=20.0)
    
    msg, _ = broker.broadcast_message(v1, [v1, v2], sim_time=1.0)
    
    # Process at sim_time = 1.01 (10ms later): message should NOT be delivered yet (latency is ~50ms)
    broker.process_transit_queue(current_sim_time=1.01)
    assert broker.total_messages_delivered == 0
    assert "V-1" not in broker.received_tables.get("V-2", {})
    
    # Process at sim_time = 1.06 (60ms later): message should now be delivered
    broker.process_transit_queue(current_sim_time=1.06)
    assert broker.total_messages_delivered == 1
    assert "V-1" in broker.received_tables["V-2"]
    rec = broker.received_tables["V-2"]["V-1"]
    assert rec.message.sequence_number == 1
    assert rec.is_stale is False

def test_packet_loss_simulation():
    # 100% packet loss
    settings = SimulationSettings(communication_range_m=200.0, packet_loss_percent=100.0, network_latency_ms=10.0)
    broker = V2VCommunicationBroker(settings)
    
    v1 = VehicleState(vehicle_id="V-1", x=50.0, y=20.0, speed_ms=20.0)
    v2 = VehicleState(vehicle_id="V-2", x=100.0, y=20.0, speed_ms=20.0)
    
    broker.broadcast_message(v1, [v1, v2], sim_time=1.0)
    assert broker.total_messages_dropped_loss == 1
    assert len(broker.transit_queue) == 0
    assert broker.get_delivery_ratio() == 0.0

def test_stale_telemetry_detection():
    settings = SimulationSettings(stale_message_threshold_s=0.5, packet_loss_percent=0.0, network_latency_ms=10.0)
    broker = V2VCommunicationBroker(settings)
    
    v1 = VehicleState(vehicle_id="V-1", x=50.0, y=20.0, speed_ms=20.0)
    v2 = VehicleState(vehicle_id="V-2", x=100.0, y=20.0, speed_ms=20.0)
    
    broker.broadcast_message(v1, [v1, v2], sim_time=1.0)
    broker.process_transit_queue(current_sim_time=1.02)
    
    # Check freshness at 1.2s (delta = 0.2s < 0.5s): Fresh
    broker.update_freshness(current_sim_time=1.2)
    assert broker.received_tables["V-2"]["V-1"].is_stale is False
    
    # Check freshness at 1.8s (delta = 0.8s > 0.5s): Stale!
    broker.update_freshness(current_sim_time=1.8)
    assert broker.received_tables["V-2"]["V-1"].is_stale is True
    assert broker.get_total_stale_count() == 1
