export interface VehicleDimensions {
  length_m: number;
  width_m: number;
}

export interface VehicleState {
  vehicle_id: string;
  x: number;
  y: number;
  speed_kmh: number;
  speed_ms: number;
  target_speed_ms: number;
  heading: number;
  acceleration: number;
  braking: boolean;
  emergency_braking: boolean;
  lane_id: number;
  dimensions: VehicleDimensions;
  communication_range: number;
  risk_level: 'SAFE' | 'WARNING' | 'CRITICAL';
  active_warning_reason?: string | null;
  partner_vehicle_id?: string | null;
  ttc_seconds?: number | null;
  color: string;
  driver_profile: string;
  updated_at: number;
}

export interface V2VMessage {
  message_id: string;
  sender_id: string;
  sequence_number: number;
  timestamp: number;
  position_x: number;
  position_y: number;
  speed_kmh: number;
  speed_ms: number;
  heading: number;
  acceleration: number;
  brake_active: boolean;
  emergency_brake_active: boolean;
  lane_id: number;
  event_flags: string[];
}

export interface ReceivedMessageRecord {
  message: V2VMessage;
  received_at: number;
  latency_ms: number;
  distance_at_reception_m: number;
  is_stale: boolean;
}

export interface SafetyEvent {
  event_id: string;
  timestamp: number;
  event_type: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  primary_vehicle_id: string;
  secondary_vehicle_id?: string | null;
  description: string;
  ttc_seconds?: number | null;
  distance_m?: number | null;
}

export interface PerVehicleCommMetrics {
  vehicle_id: string;
  messages_transmitted: number;
  messages_received: number;
  messages_dropped: number;
  stale_messages_count: number;
  neighbors_in_range_count: number;
  last_seq_received: Record<string, number>;
}

export interface SimulationMetrics {
  simulation_time_seconds: number;
  active_vehicles: number;
  v2v_messages_per_second: number;
  current_collision_warnings: number;
  current_critical_alerts: number;
  average_latency_ms: number;
  packet_delivery_percentage: number;
  total_messages_sent: number;
  total_messages_delivered: number;
  total_messages_dropped: number;
  stale_telemetry_count: number;
  measured_processing_time_ms: number;
  per_vehicle_metrics: Record<string, PerVehicleCommMetrics>;
}

export interface SimulationSettings {
  time_step: number;
  speed_multiplier: number;
  vehicle_count: number;
  communication_range_m: number;
  message_frequency_hz: number;
  packet_loss_percent: number;
  network_latency_ms: number;
  ttc_critical_threshold_s: number;
  ttc_warning_threshold_s: number;
  safe_headway_distance_m: number;
  emergency_brake_decel_threshold: number;
  stale_message_threshold_s: number;
  road_length_m: number;
  lane_width_m: number;
}

export interface SimulationSnapshot {
  status: 'STOPPED' | 'RUNNING' | 'PAUSED';
  sim_time: number;
  scenario_id: string;
  is_intersection: boolean;
  vehicles: VehicleState[];
  metrics: SimulationMetrics;
  recent_events: SafetyEvent[];
  settings: SimulationSettings;
}

export interface ScenarioInfo {
  id: string;
  name: string;
  category: string;
  description: string;
  expected_outcome: string;
  is_intersection: boolean;
}

export interface NetworkTransmissionLog {
  packet_id: string;
  sender_id: string;
  target_id: string;
  sent_at: number;
  delivered_at?: number | null;
  status: string;
  latency_ms: number;
  distance_m: number;
}
