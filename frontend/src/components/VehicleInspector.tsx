import React, { useState, useEffect } from 'react';
import { 
  X, 
  Flame, 
  Compass, 
  Gauge, 
  Radio, 
  ShieldAlert, 
  CheckCircle2, 
  Activity, 
  AlertTriangle,
  ArrowUpRight,
  Zap
} from 'lucide-react';
import { VehicleState, SafetyEvent, ReceivedMessageRecord } from '../types/simulation';
import { api } from '../services/api';

interface VehicleInspectorProps {
  vehicle: VehicleState | null;
  allVehicles: VehicleState[];
  events: SafetyEvent[];
  onClose: () => void;
  onSelectVehicle: (id: string) => void;
  onEmergencyBrake: (id: string) => void;
  communicationRange: number;
}

export const VehicleInspector: React.FC<VehicleInspectorProps> = ({
  vehicle,
  allVehicles,
  events,
  onClose,
  onSelectVehicle,
  onEmergencyBrake,
  communicationRange,
}) => {
  const [receivedMessages, setReceivedMessages] = useState<Record<string, ReceivedMessageRecord>>({});
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);

  useEffect(() => {
    if (!vehicle) return;
    let isMounted = true;

    const fetchMsgs = async () => {
      try {
        const res = await api.fetchVehicleMessages(vehicle.vehicle_id);
        if (isMounted) {
          setReceivedMessages(res.received_messages || {});
        }
      } catch (e) {
        // Silent catch for live poll
      }
    };

    fetchMsgs();
    const interval = setInterval(fetchMsgs, 500);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [vehicle?.vehicle_id]);

  if (!vehicle) return null;

  // Compute nearby vehicles in range
  const neighborsInRange = allVehicles.filter((other) => {
    if (other.vehicle_id === vehicle.vehicle_id) return false;
    const dist = Math.hypot(vehicle.x - other.x, vehicle.y - other.y);
    return dist <= Math.min(vehicle.communication_range, communicationRange);
  });

  // Filter events involving this vehicle
  const relevantEvents = events.filter(
    (e) => e.primary_vehicle_id === vehicle.vehicle_id || e.secondary_vehicle_id === vehicle.vehicle_id
  );

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-charcoal-900 border-l border-charcoal-750 shadow-2xl flex flex-col backdrop-blur-xl">
      {/* Drawer Header */}
      <div className="p-4 border-b border-charcoal-800 bg-charcoal-850 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className="w-4 h-4 rounded-full shadow-[0_0_10px_currentColor]"
            style={{ backgroundColor: vehicle.color, color: vehicle.color }}
          />
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold font-mono text-white">{vehicle.vehicle_id}</h2>
              <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold uppercase ${
                vehicle.risk_level === 'CRITICAL' ? 'bg-rose-950 text-rose-400 border border-rose-500' :
                vehicle.risk_level === 'WARNING' ? 'bg-amber-950 text-amber-400 border border-amber-500' :
                'bg-emerald-950 text-emerald-400 border border-emerald-500'
              }`}>
                {vehicle.risk_level}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Lane {vehicle.lane_id} | Driver: {vehicle.driver_profile}
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-charcoal-750 transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Drawer Scroll Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-xs">
        {/* Manual Emergency Brake Actuation Banner */}
        <div className="p-3 rounded-xl bg-gradient-to-r from-rose-950/40 to-charcoal-850 border border-rose-500/40 flex items-center justify-between gap-3">
          <div>
            <div className="text-white font-bold flex items-center gap-1.5 text-xs">
              <Zap className="w-4 h-4 text-rose-400" />
              <span>Actuate Emergency Brake</span>
            </div>
            <p className="text-[11px] text-slate-400 font-sans mt-0.5">
              Simulates sudden driver intervention or obstacle detection (-8.5 m/s²).
            </p>
          </div>

          <button
            onClick={() => onEmergencyBrake(vehicle.vehicle_id)}
            disabled={vehicle.emergency_braking}
            className={`px-3 py-2 rounded-lg font-bold uppercase text-[11px] tracking-wider transition ${
              vehicle.emergency_braking
                ? 'bg-rose-950 text-rose-400 border border-rose-600/50 cursor-not-allowed opacity-80'
                : 'bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-900/40 active:scale-95'
            }`}
          >
            {vehicle.emergency_braking ? 'BRAKE ENGAGED' : 'TRIGGER BRAKE'}
          </button>
        </div>

        {/* Dynamic Telemetry Matrix */}
        <div className="grid grid-cols-2 gap-2.5">
          <div className="bg-charcoal-850 p-2.5 rounded-lg border border-charcoal-750">
            <div className="flex items-center gap-1.5 text-slate-400 text-[10px] mb-1">
              <Gauge className="w-3.5 h-3.5 text-cyan-400" />
              <span>SPEED / TARGET</span>
            </div>
            <div className="text-base font-bold text-white">
              {vehicle.speed_kmh} <span className="text-[10px] text-slate-400">km/h</span>
            </div>
            <div className="text-[10px] text-slate-500">
              Target: {(vehicle.target_speed_ms * 3.6).toFixed(0)} km/h
            </div>
          </div>

          <div className="bg-charcoal-850 p-2.5 rounded-lg border border-charcoal-750">
            <div className="flex items-center gap-1.5 text-slate-400 text-[10px] mb-1">
              <Activity className="w-3.5 h-3.5 text-blue-400" />
              <span>ACCELERATION</span>
            </div>
            <div className={`text-base font-bold ${
              vehicle.acceleration < -4.0 ? 'text-rose-400' : vehicle.acceleration < 0 ? 'text-amber-400' : 'text-emerald-400'
            }`}>
              {vehicle.acceleration.toFixed(2)} <span className="text-[10px] text-slate-400">m/s²</span>
            </div>
            <div className="text-[10px] text-slate-500">
              {vehicle.emergency_braking ? 'EEBL Trigger Active' : vehicle.braking ? 'Brakes Applied' : 'Cruising'}
            </div>
          </div>

          <div className="bg-charcoal-850 p-2.5 rounded-lg border border-charcoal-750">
            <div className="flex items-center gap-1.5 text-slate-400 text-[10px] mb-1">
              <Compass className="w-3.5 h-3.5 text-indigo-400" />
              <span>HEADING / ORIENTATION</span>
            </div>
            <div className="text-base font-bold text-white">
              {vehicle.heading.toFixed(0)}°
            </div>
            <div className="text-[10px] text-slate-500">
              {vehicle.heading === 0 ? 'East (+X)' : vehicle.heading === 90 ? 'North (+Y)' : `${vehicle.heading}°`}
            </div>
          </div>

          <div className="bg-charcoal-850 p-2.5 rounded-lg border border-charcoal-750">
            <div className="flex items-center gap-1.5 text-slate-400 text-[10px] mb-1">
              <Radio className="w-3.5 h-3.5 text-cyan-400" />
              <span>COORDINATES (X, Y)</span>
            </div>
            <div className="text-xs font-bold text-slate-200 mt-1">
              X: {vehicle.x.toFixed(1)}m
            </div>
            <div className="text-xs font-bold text-slate-200">
              Y: {vehicle.y.toFixed(1)}m
            </div>
          </div>
        </div>

        {/* Warning Reason if Active */}
        {vehicle.active_warning_reason && (
          <div className={`p-3 rounded-lg border ${
            vehicle.risk_level === 'CRITICAL'
              ? 'bg-rose-950/40 border-rose-500/50 text-rose-300'
              : 'bg-amber-950/40 border-amber-500/50 text-amber-300'
          }`}>
            <div className="flex items-center gap-2 font-bold mb-1">
              <AlertTriangle className="w-4 h-4" />
              <span>{vehicle.risk_level} SAFETY ALERT</span>
            </div>
            <p className="text-[11px] font-sans leading-relaxed text-slate-200">
              {vehicle.active_warning_reason}
            </p>
            {vehicle.partner_vehicle_id && (
              <div className="mt-2 pt-2 border-t border-charcoal-700/60 flex items-center justify-between text-[11px]">
                <span>Hazard Partner:</span>
                <button
                  onClick={() => onSelectVehicle(vehicle.partner_vehicle_id!)}
                  className="text-cyan-400 hover:underline font-bold"
                >
                  {vehicle.partner_vehicle_id}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Nearby Vehicles in V2V Range */}
        <div className="bg-charcoal-850 rounded-lg p-3 border border-charcoal-750">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-300 font-semibold text-xs">
              Nearby V2V Neighbors ({neighborsInRange.length})
            </span>
            <span className="text-slate-500 text-[10px]">Within {communicationRange}m</span>
          </div>

          {neighborsInRange.length === 0 ? (
            <p className="text-slate-500 text-[11px] py-1">No other vehicles currently in wireless range.</p>
          ) : (
            <div className="space-y-1.5">
              {neighborsInRange.map((n) => {
                const dist = Math.hypot(vehicle.x - n.x, vehicle.y - n.y);
                return (
                  <div
                    key={n.vehicle_id}
                    onClick={() => onSelectVehicle(n.vehicle_id)}
                    className="flex items-center justify-between p-2 rounded bg-charcoal-900/80 border border-charcoal-750 hover:border-cyan-500/50 cursor-pointer transition"
                  >
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: n.color }} />
                      <span className="font-bold text-white">{n.vehicle_id}</span>
                      <span className="text-slate-400 text-[10px]">{n.speed_kmh} km/h</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-cyan-400 font-semibold">{dist.toFixed(1)}m</span>
                      <ArrowUpRight className="w-3.5 h-3.5 text-slate-500" />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Received V2V Basic Safety Messages Table */}
        <div className="bg-charcoal-850 rounded-lg p-3 border border-charcoal-750">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-300 font-semibold text-xs">
              Received BSM Table (Cooperative State)
            </span>
            <span className="text-cyan-400 text-[10px]">
              {Object.keys(receivedMessages).length} senders
            </span>
          </div>

          {Object.keys(receivedMessages).length === 0 ? (
            <p className="text-slate-500 text-[11px] py-2">Awaiting incoming V2V packets...</p>
          ) : (
            <div className="space-y-2">
              {Object.values(receivedMessages).map((rec) => (
                <div
                  key={rec.message.message_id}
                  className="p-2 rounded bg-charcoal-900 border border-charcoal-750 text-[11px]"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-cyan-300">{rec.message.sender_id}</span>
                    <span className={`px-1.5 py-0.2 rounded text-[9px] font-bold ${
                      rec.is_stale ? 'bg-rose-950 text-rose-400 border border-rose-500/50' : 'bg-emerald-950 text-emerald-400'
                    }`}>
                      {rec.is_stale ? 'STALE' : 'FRESH'}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-1 text-[10px] text-slate-400">
                    <div>Seq: <span className="text-slate-200">#{rec.message.sequence_number}</span></div>
                    <div>Lat: <span className="text-slate-200">{rec.latency_ms}ms</span></div>
                    <div>Dist: <span className="text-slate-200">{rec.distance_at_reception_m}m</span></div>
                    <div>Speed: <span className="text-slate-200">{rec.message.speed_kmh} km/h</span></div>
                  </div>

                  {rec.message.emergency_brake_active && (
                    <div className="mt-1 text-[10px] text-rose-400 font-bold flex items-center gap-1">
                      <Flame className="w-3 h-3" /> EEBL Flag Transmitted!
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Events involving vehicle */}
        <div className="bg-charcoal-850 rounded-lg p-3 border border-charcoal-750">
          <span className="text-slate-300 font-semibold text-xs mb-2 block">
            Vehicle History Events ({relevantEvents.length})
          </span>
          {relevantEvents.length === 0 ? (
            <p className="text-slate-500 text-[11px]">No specific incident events recorded.</p>
          ) : (
            <div className="space-y-1.5 max-h-36 overflow-y-auto">
              {relevantEvents.slice(-5).reverse().map((evt) => (
                <div key={evt.event_id} className="text-[10px] p-1.5 rounded bg-charcoal-900 border border-charcoal-750">
                  <div className="flex items-center justify-between text-slate-400">
                    <span className="font-semibold text-slate-300">{evt.event_type}</span>
                    <span>{evt.timestamp.toFixed(2)}s</span>
                  </div>
                  <p className="text-slate-400 text-[10px] mt-0.5 font-sans truncate">{evt.description}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
