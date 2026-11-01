import React from 'react';
import { Car, Radio, AlertTriangle, Flame, Clock, CheckCircle2 } from 'lucide-react';
import { SimulationMetrics } from '../types/simulation';

interface SummaryCardsProps {
  metrics: SimulationMetrics | null;
  vehicleCount: number;
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({ metrics, vehicleCount }) => {
  const activeVehicles = metrics?.active_vehicles ?? vehicleCount;
  const msgRate = metrics?.v2v_messages_per_second ?? 0.0;
  const warnings = metrics?.current_collision_warnings ?? 0;
  const critical = metrics?.current_critical_alerts ?? 0;
  const avgLatency = metrics?.average_latency_ms ?? 0.0;
  const deliveryRatio = metrics?.packet_delivery_percentage ?? 100.0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">
      {/* 1. Active Vehicles */}
      <div className="bg-charcoal-900 border border-charcoal-800 rounded-xl p-3.5 relative overflow-hidden group hover:border-cyan-500/30 transition shadow-sm">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[11px] font-medium tracking-wide uppercase">Active Vehicles</span>
          <div className="p-1.5 rounded-lg bg-blue-950/60 border border-blue-500/20 text-blue-400">
            <Car className="w-4 h-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-slate-100">{activeVehicles}</span>
          <span className="text-[10px] text-cyan-400 font-mono">SDV Nodes</span>
        </div>
        <div className="mt-2 text-[11px] text-slate-500 flex items-center justify-between">
          <span>Kinematic Model</span>
          <span className="text-slate-400 font-mono">20 Hz Loop</span>
        </div>
      </div>

      {/* 2. V2V Msg/Sec */}
      <div className="bg-charcoal-900 border border-charcoal-800 rounded-xl p-3.5 relative overflow-hidden group hover:border-cyan-500/30 transition shadow-sm">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[11px] font-medium tracking-wide uppercase">V2V Msg Rate</span>
          <div className="p-1.5 rounded-lg bg-cyan-950/60 border border-cyan-500/20 text-cyan-400">
            <Radio className="w-4 h-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-cyan-300">{msgRate.toFixed(1)}</span>
          <span className="text-[10px] text-slate-400 font-mono">msg/sec</span>
        </div>
        <div className="mt-2 text-[11px] text-slate-500 flex items-center justify-between">
          <span>SAE J2735 Standard</span>
          <span className="text-cyan-400 font-mono">BSM Broadcast</span>
        </div>
      </div>

      {/* 3. Collision Warnings */}
      <div className={`bg-charcoal-900 border rounded-xl p-3.5 relative overflow-hidden transition shadow-sm ${
        warnings > 0 ? 'border-amber-500/50 bg-amber-950/10' : 'border-charcoal-800'
      }`}>
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[11px] font-medium tracking-wide uppercase">Collision Warnings</span>
          <div className={`p-1.5 rounded-lg border ${
            warnings > 0 ? 'bg-amber-950/70 border-amber-500/40 text-amber-400' : 'bg-charcoal-800 border-charcoal-700 text-slate-400'
          }`}>
            <AlertTriangle className="w-4 h-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className={`text-2xl font-bold font-mono ${warnings > 0 ? 'text-amber-400' : 'text-slate-100'}`}>
            {warnings}
          </span>
          <span className="text-[10px] text-slate-400 font-mono">TTC &lt; 4.5s</span>
        </div>
        <div className="mt-2 text-[11px] text-slate-500 flex items-center justify-between">
          <span>Hysteresis Filter</span>
          <span className="text-amber-400/80 font-mono">Active</span>
        </div>
      </div>

      {/* 4. Critical Alerts */}
      <div className={`bg-charcoal-900 border rounded-xl p-3.5 relative overflow-hidden transition shadow-sm ${
        critical > 0 ? 'border-rose-500/60 bg-rose-950/20 animate-critical-pulse' : 'border-charcoal-800'
      }`}>
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[11px] font-medium tracking-wide uppercase">Critical Alerts</span>
          <div className={`p-1.5 rounded-lg border ${
            critical > 0 ? 'bg-rose-950 border-rose-500 text-rose-400' : 'bg-charcoal-800 border-charcoal-700 text-slate-400'
          }`}>
            <Flame className="w-4 h-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className={`text-2xl font-bold font-mono ${critical > 0 ? 'text-rose-400' : 'text-slate-100'}`}>
            {critical}
          </span>
          <span className="text-[10px] text-slate-400 font-mono">TTC &lt; 2.5s</span>
        </div>
        <div className="mt-2 text-[11px] text-slate-500 flex items-center justify-between">
          <span>Hazard Mitigation</span>
          <span className={`font-mono ${critical > 0 ? 'text-rose-400 font-semibold' : 'text-slate-400'}`}>
            {critical > 0 ? 'INTERVENTION' : 'Nominal'}
          </span>
        </div>
      </div>

      {/* 5. Average Latency */}
      <div className="bg-charcoal-900 border border-charcoal-800 rounded-xl p-3.5 relative overflow-hidden group hover:border-cyan-500/30 transition shadow-sm">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[11px] font-medium tracking-wide uppercase">Avg Network Latency</span>
          <div className="p-1.5 rounded-lg bg-indigo-950/60 border border-indigo-500/20 text-indigo-400">
            <Clock className="w-4 h-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-slate-100">{avgLatency.toFixed(1)}</span>
          <span className="text-[10px] text-slate-400 font-mono">ms</span>
        </div>
        <div className="mt-2 text-[11px] text-slate-500 flex items-center justify-between">
          <span>RF Propagation</span>
          <span className="text-indigo-400 font-mono">Queue Delay</span>
        </div>
      </div>

      {/* 6. Packet Delivery Ratio */}
      <div className="bg-charcoal-900 border border-charcoal-800 rounded-xl p-3.5 relative overflow-hidden group hover:border-cyan-500/30 transition shadow-sm">
        <div className="flex items-center justify-between text-slate-400 mb-1.5">
          <span className="text-[11px] font-medium tracking-wide uppercase">Delivery Ratio</span>
          <div className={`p-1.5 rounded-lg border ${
            deliveryRatio > 85 ? 'bg-emerald-950/60 border-emerald-500/20 text-emerald-400' : 'bg-rose-950/60 border-rose-500/20 text-rose-400'
          }`}>
            <CheckCircle2 className="w-4 h-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className={`text-2xl font-bold font-mono ${deliveryRatio > 85 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {deliveryRatio.toFixed(1)}%
          </span>
          <span className="text-[10px] text-slate-400 font-mono">QoS</span>
        </div>
        <div className="mt-2 text-[11px] text-slate-500 flex items-center justify-between">
          <span>Packet Loss</span>
          <span className="text-slate-400 font-mono">{metrics?.total_messages_dropped ?? 0} dropped</span>
        </div>
      </div>
    </div>
  );
};
