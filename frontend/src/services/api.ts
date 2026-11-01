import { SimulationSnapshot, VehicleState, SafetyEvent, SimulationMetrics, ScenarioInfo, NetworkTransmissionLog, SimulationSettings } from '../types/simulation';

const BASE_URL = '/api';

export const api = {
  async fetchStatus(): Promise<SimulationSnapshot> {
    const res = await fetch(`${BASE_URL}/simulation/status`);
    if (!res.ok) throw new Error('Failed to fetch simulation status');
    return res.json();
  },

  async fetchVehicles(): Promise<VehicleState[]> {
    const res = await fetch(`${BASE_URL}/vehicles`);
    if (!res.ok) throw new Error('Failed to fetch vehicles');
    return res.json();
  },

  async fetchVehicleMessages(vehicleId: string) {
    const res = await fetch(`${BASE_URL}/vehicles/${vehicleId}/messages`);
    if (!res.ok) throw new Error(`Failed to fetch messages for vehicle ${vehicleId}`);
    return res.json();
  },

  async fetchEvents(limit = 50): Promise<SafetyEvent[]> {
    const res = await fetch(`${BASE_URL}/events?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch safety events');
    return res.json();
  },

  async fetchMetrics(): Promise<SimulationMetrics> {
    const res = await fetch(`${BASE_URL}/metrics`);
    if (!res.ok) throw new Error('Failed to fetch simulation metrics');
    return res.json();
  },

  async fetchScenarios(): Promise<ScenarioInfo[]> {
    const res = await fetch(`${BASE_URL}/scenarios`);
    if (!res.ok) throw new Error('Failed to fetch scenarios');
    return res.json();
  },

  async fetchMessageLogs(limit = 50): Promise<NetworkTransmissionLog[]> {
    const res = await fetch(`${BASE_URL}/messages/logs?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch message logs');
    return res.json();
  },

  async start(): Promise<void> {
    await fetch(`${BASE_URL}/simulation/start`, { method: 'POST' });
  },

  async pause(): Promise<void> {
    await fetch(`${BASE_URL}/simulation/pause`, { method: 'POST' });
  },

  async resume(): Promise<void> {
    await fetch(`${BASE_URL}/simulation/resume`, { method: 'POST' });
  },

  async stop(): Promise<void> {
    await fetch(`${BASE_URL}/simulation/stop`, { method: 'POST' });
  },

  async reset(): Promise<void> {
    await fetch(`${BASE_URL}/simulation/reset`, { method: 'POST' });
  },

  async selectScenario(scenarioId: string): Promise<void> {
    await fetch(`${BASE_URL}/simulation/scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_id: scenarioId }),
    });
  },

  async updateSettings(settings: Partial<SimulationSettings>): Promise<void> {
    await fetch(`${BASE_URL}/simulation/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings),
    });
  },

  async triggerEmergencyBrake(vehicleId: string): Promise<void> {
    await fetch(`${BASE_URL}/vehicles/${vehicleId}/emergency-brake`, {
      method: 'POST',
    });
  },
};
