import React from 'react';
import { X, Activity, Radio, Wifi, AlertTriangle, ShieldCheck, Clock, Server } from 'lucide-react';
import { SimulationMetrics, SimulationSettings } from '../types/simulation';

interface NetworkAnalyticsModalProps {
  isOpen: boolean;
  onClose: () => void;
  metrics: SimulationMetrics | null;
  settings: SimulationSettings | null;
}

export const NetworkAnalyticsModal: React.FC<NetworkAnalyticsModalProps> = ({
  isOpen,
  onClose,
  metrics,
  settings,
}) => {
  if (!isOpen) return null;

  const perVehMap = metrics?.per_vehicle_metrics || {};

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-charcoal-900 border border-charcoal-750 rounded-2xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden font-mono">
        {/* Header */}
        <div className="p-4 border-b border-charcoal-800 bg-charcoal-850 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-blue-950/80 border border-blue-500/30 text-blue-400">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-wide">
                V2V Wireless Network Analytics & QoS Telemetry
              </h2>
              <p className="text-xs text-slate-400 font-sans">
                Real-time tracking of simulated radio propagation, packet loss, and queue delays.
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

        {/* Modal Scroll Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5 text-xs">
          {/* Key Metric Gauges */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-charcoal-850 border border-charcoal-750">
              <div className="text-slate-400 text-[10px] uppercase">Total Broadcast Packets</div>
              <div className="text-xl font-bold text-white mt-1">
                {metrics?.total_messages_sent ?? 0}
              </div>
              <div className="text-[10px] text-cyan-400 mt-0.5">
                Rate: {(metrics?.v2v_messages_per_second ?? 0).toFixed(1)} Hz
              </div>
            </div>

            <div className="p-3 rounded-xl bg-charcoal-850 border border-charcoal-750">
              <div className="text-slate-400 text-[10px] uppercase">Delivered Successfully</div>
              <div className="text-xl font-bold text-emerald-400 mt-1">
                {metrics?.total_messages_delivered ?? 0}
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Ratio: {(metrics?.packet_delivery_percentage ?? 100).toFixed(1)}%
              </div>
            </div>

            <div className="p-3 rounded-xl bg-charcoal-850 border border-charcoal-750">
              <div className="text-slate-400 text-[10px] uppercase">Dropped (Loss / Fade)</div>
              <div className={`text-xl font-bold mt-1 ${
                (metrics?.total_messages_dropped ?? 0) > 0 ? 'text-rose-400' : 'text-slate-200'
              }`}>
                {metrics?.total_messages_dropped ?? 0}
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Configured Loss: {settings?.packet_loss_percent.toFixed(0) ?? 0}%
              </div>
            </div>

            <div className="p-3 rounded-xl bg-charcoal-850 border border-charcoal-750">
              <div className="text-slate-400 text-[10px] uppercase">Stale Telemetry Packets</div>
              <div className={`text-xl font-bold mt-1 ${
                (metrics?.stale_telemetry_count ?? 0) > 0 ? 'text-amber-400' : 'text-slate-200'
              }`}>
                {metrics?.stale_telemetry_count ?? 0}
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Expiry: &gt; {settings?.stale_message_threshold_s ?? 0.8}s
              </div>
            </div>
          </div>

          {/* Latency & Processing Breakdown */}
          <div className="p-4 rounded-xl bg-charcoal-850 border border-charcoal-750">
            <h3 className="font-bold text-slate-200 mb-3 flex items-center gap-2">
              <Clock className="w-4 h-4 text-indigo-400" />
              <span>Latency and Processing Performance Breakdown</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-3 rounded-lg bg-charcoal-900 border border-charcoal-750">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-slate-300 font-semibold">Simulated Wireless Propagation Latency:</span>
                  <span className="text-indigo-400 font-bold">{metrics?.average_latency_ms.toFixed(1)} ms</span>
                </div>
                <p className="text-[11px] text-slate-400 font-sans">
                  Configured queue delay model ({settings?.network_latency_ms} ms ± 10% RF jitter) representing physical DSRC/C-V2X channel delays.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-charcoal-900 border border-charcoal-750">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-slate-300 font-semibold">Backend Engine Execution Time:</span>
                  <span className="text-cyan-400 font-bold">{metrics?.measured_processing_time_ms.toFixed(2)} ms</span>
                </div>
                <p className="text-[11px] text-slate-400 font-sans">
                  Authoritative physics step and safety evaluation tick duration (well within the 50ms real-time budget).
                </p>
              </div>
            </div>
          </div>

          {/* Per-Vehicle Node Communication Matrix */}
          <div className="p-4 rounded-xl bg-charcoal-850 border border-charcoal-750">
            <h3 className="font-bold text-slate-200 mb-3 flex items-center gap-2">
              <Radio className="w-4 h-4 text-cyan-400" />
              <span>Per-Vehicle Communication Health & Status Matrix</span>
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-charcoal-700 text-slate-400 text-[10px] uppercase">
                    <th className="py-2 px-3">Vehicle Node</th>
                    <th className="py-2 px-3">Transmitted</th>
                    <th className="py-2 px-3">Received</th>
                    <th className="py-2 px-3">Dropped</th>
                    <th className="py-2 px-3">Stale Count</th>
                    <th className="py-2 px-3">In-Range Neighbors</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-charcoal-750">
                  {Object.keys(perVehMap).length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-4 text-center text-slate-500">
                        Gathering per-vehicle transmission telemetry...
                      </td>
                    </tr>
                  ) : (
                    Object.values(perVehMap).map((m) => (
                      <tr key={m.vehicle_id} className="hover:bg-charcoal-800/50">
                        <td className="py-2 px-3 font-bold text-cyan-300">{m.vehicle_id}</td>
                        <td className="py-2 px-3 text-slate-200">{m.messages_transmitted}</td>
                        <td className="py-2 px-3 text-emerald-400">{m.messages_received}</td>
                        <td className="py-2 px-3 text-rose-400">{m.messages_dropped}</td>
                        <td className="py-2 px-3 text-amber-400">{m.stale_messages_count}</td>
                        <td className="py-2 px-3 text-blue-400">{m.neighbors_in_range_count}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
