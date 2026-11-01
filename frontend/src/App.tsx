import React, { useState, useEffect, useRef } from 'react';
import { TopNav } from './components/TopNav';
import { SummaryCards } from './components/SummaryCards';
import { ScenarioBanner } from './components/ScenarioBanner';
import { RoadCanvas } from './components/RoadCanvas';
import { LiveEventFeed } from './components/LiveEventFeed';
import { TelemetryCharts, TelemetryPoint } from './components/TelemetryCharts';
import { VehicleInspector } from './components/VehicleInspector';
import { NetworkAnalyticsModal } from './components/NetworkAnalyticsModal';
import { MessageInspectorModal } from './components/MessageInspectorModal';
import { SimulationSettingsModal } from './components/SimulationSettingsModal';

import { SimulationSnapshot, ScenarioInfo, VehicleState } from './types/simulation';
import { wsClient } from './services/websocket';
import { api } from './services/api';

export function App() {
  const [snapshot, setSnapshot] = useState<SimulationSnapshot | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [scenarios, setScenarios] = useState<ScenarioInfo[]>([]);
  const [selectedVehicleId, setSelectedVehicleId] = useState<string | null>('V2V-01');

  // Modal open states
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isAnalyticsOpen, setIsAnalyticsOpen] = useState(false);
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);

  // Real-time telemetry sliding history
  const [history, setHistory] = useState<TelemetryPoint[]>([]);
  const lastHistorySimTimeRef = useRef<number>(0);

  // Initialize Scenarios & WebSocket connection
  useEffect(() => {
    // 1. Fetch scenario definitions
    api.fetchScenarios().then((data) => setScenarios(data)).catch(() => {});

    // 2. Fetch initial snapshot via REST as fast fallback
    api.fetchStatus().then((initial) => {
      setSnapshot(initial);
    }).catch(() => {});

    // 3. Connect to WebSocket stream
    const unsubConn = wsClient.onConnectionChange((connected) => {
      setIsConnected(connected);
    });

    const unsubMsg = wsClient.subscribe((data) => {
      setSnapshot(data);

      // Sample telemetry points for charts every ~0.5s of simulation time
      if (Math.abs(data.sim_time - lastHistorySimTimeRef.current) >= 0.4) {
        lastHistorySimTimeRef.current = data.sim_time;

        const point: TelemetryPoint = {
          time: `${data.sim_time.toFixed(1)}s`,
          simTime: data.sim_time,
          msgRate: Math.round(data.metrics.v2v_messages_per_second * 10) / 10,
          latency: Math.round(data.metrics.average_latency_ms * 10) / 10,
          warnings: data.metrics.current_collision_warnings,
          critical: data.metrics.current_critical_alerts,
        };

        // Add speeds for each vehicle
        data.vehicles.forEach((v) => {
          point[v.vehicle_id] = Math.round(v.speed_kmh);
        });

        setHistory((prev) => {
          const next = [...prev, point];
          return next.slice(-40); // keep rolling 40 points
        });
      }
    });

    return () => {
      unsubConn();
      unsubMsg();
    };
  }, []);

  // Controls Handlers
  const handlePlay = async () => {
    wsClient.sendCommand({ type: 'start' });
    try {
      await api.start();
    } catch (e) {}
  };

  const handlePause = async () => {
    wsClient.sendCommand({ type: 'pause' });
    try {
      await api.pause();
    } catch (e) {}
  };

  const handleReset = async () => {
    setHistory([]);
    wsClient.sendCommand({ type: 'reset' });
    try {
      await api.reset();
    } catch (e) {}
  };

  const handleSelectScenario = async (scenarioId: string) => {
    setHistory([]);
    wsClient.sendCommand({ type: 'scenario', scenario_id: scenarioId });
    try {
      await api.selectScenario(scenarioId);
    } catch (e) {}
  };

  const handleEmergencyBrake = async (vehicleId: string) => {
    wsClient.sendCommand({ type: 'emergency_brake', vehicle_id: vehicleId });
    try {
      await api.triggerEmergencyBrake(vehicleId);
    } catch (e) {}
  };

  const currentScenarioInfo = scenarios.find((s) => s.id === (snapshot?.scenario_id || 'normal_traffic')) || null;
  const selectedVehicle = snapshot?.vehicles.find((v) => v.vehicle_id === selectedVehicleId) || null;
  const vehicleIds = snapshot?.vehicles.map((v) => v.vehicle_id) || [];

  return (
    <div className="min-h-screen bg-[#070A10] text-slate-100 flex flex-col font-sans">
      {/* Top Header */}
      <TopNav
        snapshot={snapshot}
        isConnected={isConnected}
        scenarios={scenarios}
        onPlay={handlePlay}
        onPause={handlePause}
        onReset={handleReset}
        onSelectScenario={handleSelectScenario}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenAnalytics={() => setIsAnalyticsOpen(true)}
        onOpenInspector={() => setIsInspectorOpen(true)}
      />

      {/* Main Automotive Dashboard Content */}
      <main className="flex-1 max-w-[1700px] w-full mx-auto p-4 sm:p-5 space-y-4">
        {/* Section 1: Real-time Telemetry Stat Cards */}
        <SummaryCards
          metrics={snapshot?.metrics || null}
          vehicleCount={snapshot?.vehicles.length || 6}
        />

        {/* Section 2: Active Scenario Banner & Fast Switcher */}
        <ScenarioBanner
          currentScenario={currentScenarioInfo}
          scenarios={scenarios}
          onSelectScenario={handleSelectScenario}
          onReset={handleReset}
          onStart={handlePlay}
          isRunning={snapshot?.status === 'RUNNING'}
        />

        {/* Section 3: Dual View — 2D Road Visualization & Live Event Feed */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Main 2D Road Simulation (Canvas) */}
          <div className="lg:col-span-8 flex flex-col">
            <RoadCanvas
              vehicles={snapshot?.vehicles || []}
              isIntersection={snapshot?.is_intersection || false}
              selectedVehicleId={selectedVehicleId}
              onSelectVehicle={(id) => setSelectedVehicleId(id)}
              communicationRange={snapshot?.settings.communication_range_m || 200}
            />
          </div>

          {/* Live Safety Event Feed */}
          <div className="lg:col-span-4 flex flex-col">
            <LiveEventFeed
              events={snapshot?.recent_events || []}
              onSelectVehicle={(id) => setSelectedVehicleId(id)}
            />
          </div>
        </div>

        {/* Section 4: Real-Time Charts Panel */}
        <TelemetryCharts history={history} vehicleIds={vehicleIds} />
      </main>

      {/* Vehicle Inspector Side Drawer */}
      {selectedVehicle && (
        <VehicleInspector
          vehicle={selectedVehicle}
          allVehicles={snapshot?.vehicles || []}
          events={snapshot?.recent_events || []}
          onClose={() => setSelectedVehicleId(null)}
          onSelectVehicle={(id) => setSelectedVehicleId(id)}
          onEmergencyBrake={handleEmergencyBrake}
          communicationRange={snapshot?.settings.communication_range_m || 200}
        />
      )}

      {/* Modal 1: Network Analytics */}
      <NetworkAnalyticsModal
        isOpen={isAnalyticsOpen}
        onClose={() => setIsAnalyticsOpen(false)}
        metrics={snapshot?.metrics || null}
        settings={snapshot?.settings || null}
      />

      {/* Modal 2: BSM Packet Inspector */}
      <MessageInspectorModal
        isOpen={isInspectorOpen}
        onClose={() => setIsInspectorOpen(false)}
      />

      {/* Modal 3: Simulation & Safety Thresholds Settings */}
      <SimulationSettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        currentSettings={snapshot?.settings || null}
        onSettingsUpdated={async () => {
          const fresh = await api.fetchStatus();
          setSnapshot(fresh);
        }}
      />
    </div>
  );
}
