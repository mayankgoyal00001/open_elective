import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { SummaryCards } from './components/SummaryCards';
import { SimulationMetrics } from './types/simulation';

describe('SummaryCards Component', () => {
  const mockMetrics: SimulationMetrics = {
    simulation_time_seconds: 12.5,
    active_vehicles: 6,
    v2v_messages_per_second: 10.2,
    current_collision_warnings: 1,
    current_critical_alerts: 0,
    average_latency_ms: 22.4,
    packet_delivery_percentage: 98.5,
    total_messages_sent: 120,
    total_messages_delivered: 118,
    total_messages_dropped: 2,
    stale_telemetry_count: 0,
    measured_processing_time_ms: 1.2,
    per_vehicle_metrics: {}
  };

  it('renders all 6 automotive telemetry cards with correct values', () => {
    render(<SummaryCards metrics={mockMetrics} vehicleCount={6} />);

    expect(screen.getByText('Active Vehicles')).toBeDefined();
    expect(screen.getByText('V2V Msg Rate')).toBeDefined();
    expect(screen.getByText('Collision Warnings')).toBeDefined();
    expect(screen.getByText('Critical Alerts')).toBeDefined();
    expect(screen.getByText('Avg Network Latency')).toBeDefined();
    expect(screen.getByText('Delivery Ratio')).toBeDefined();

    // Check rendered metric values
    expect(screen.getByText('6')).toBeDefined();
    expect(screen.getByText('10.2')).toBeDefined();
    expect(screen.getByText('22.4')).toBeDefined();
    expect(screen.getByText('98.5%')).toBeDefined();
  });
});
