import React, { useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  AreaChart,
  Area,
  Legend,
} from 'recharts';
import { Gauge, Radio, AlertTriangle, Clock } from 'lucide-react';

export interface TelemetryPoint {
  time: string;
  simTime: number;
  msgRate: number;
  latency: number;
  warnings: number;
  critical: number;
  [key: string]: any; // per-vehicle speed e.g. 'V2V-01': 80
}

interface TelemetryChartsProps {
  history: TelemetryPoint[];
  vehicleIds: string[];
}

export const TelemetryCharts: React.FC<TelemetryChartsProps> = ({ history, vehicleIds }) => {
  const [activeTab, setActiveTab] = useState<'SPEED' | 'WARNINGS' | 'THROUGHPUT' | 'LATENCY'>('SPEED');

  const vehicleColors = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#06B6D4', '#EC4899'];

  return (
    <div className="bg-charcoal-900 border border-charcoal-800 rounded-xl p-4 shadow-lg">
      {/* Tab Switcher */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-charcoal-800">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-200 uppercase tracking-wide">
            Real-Time Telemetry & Network Curves
          </span>
          <span className="text-[10px] text-slate-400 font-mono">({history.length} samples)</span>
        </div>

        <div className="flex items-center gap-1 bg-charcoal-850 p-1 rounded-lg border border-charcoal-700 text-xs font-mono">
          <button
            onClick={() => setActiveTab('SPEED')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded transition ${
              activeTab === 'SPEED'
                ? 'bg-blue-600 text-white font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Gauge className="w-3.5 h-3.5" /> Speed Profiles
          </button>

          <button
            onClick={() => setActiveTab('WARNINGS')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded transition ${
              activeTab === 'WARNINGS'
                ? 'bg-amber-600 text-white font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" /> Collision Risk
          </button>

          <button
            onClick={() => setActiveTab('THROUGHPUT')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded transition ${
              activeTab === 'THROUGHPUT'
                ? 'bg-cyan-600 text-white font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Radio className="w-3.5 h-3.5" /> V2V Rate (Hz)
          </button>

          <button
            onClick={() => setActiveTab('LATENCY')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded transition ${
              activeTab === 'LATENCY'
                ? 'bg-indigo-600 text-white font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Clock className="w-3.5 h-3.5" /> Latency (ms)
          </button>
        </div>
      </div>

      {/* Charts Area */}
      <div className="h-[240px] w-full">
        {history.length < 2 ? (
          <div className="flex items-center justify-center h-full text-slate-500 text-xs font-mono">
            Accumulating live simulation telemetry points...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            {activeTab === 'SPEED' ? (
              <LineChart data={history} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="time" stroke="#64748B" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748B" unit=" km/h" tick={{ fontSize: 10 }} domain={[0, 'auto']} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0B0F19', borderColor: '#334155', fontSize: '11px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '6px' }} />
                {vehicleIds.map((id, idx) => (
                  <Line
                    key={id}
                    type="monotone"
                    dataKey={id}
                    name={id}
                    stroke={vehicleColors[idx % vehicleColors.length]}
                    dot={false}
                    strokeWidth={2}
                    isAnimationActive={false}
                  />
                ))}
              </LineChart>
            ) : activeTab === 'WARNINGS' ? (
              <AreaChart data={history} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="time" stroke="#64748B" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748B" tick={{ fontSize: 10 }} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0B0F19', borderColor: '#334155', fontSize: '11px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '6px' }} />
                <Area
                  type="monotone"
                  dataKey="critical"
                  name="Critical Alerts"
                  stroke="#EF4444"
                  fill="rgba(239, 68, 68, 0.3)"
                  strokeWidth={2}
                  isAnimationActive={false}
                />
                <Area
                  type="monotone"
                  dataKey="warnings"
                  name="Collision Warnings"
                  stroke="#F59E0B"
                  fill="rgba(245, 158, 11, 0.2)"
                  strokeWidth={2}
                  isAnimationActive={false}
                />
              </AreaChart>
            ) : activeTab === 'THROUGHPUT' ? (
              <AreaChart data={history} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="time" stroke="#64748B" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748B" unit=" Hz" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0B0F19', borderColor: '#334155', fontSize: '11px' }}
                />
                <Area
                  type="monotone"
                  dataKey="msgRate"
                  name="V2V Messages Broadcasted (Hz)"
                  stroke="#06B6D4"
                  fill="rgba(6, 182, 212, 0.2)"
                  strokeWidth={2}
                  isAnimationActive={false}
                />
              </AreaChart>
            ) : (
              <LineChart data={history} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="time" stroke="#64748B" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748B" unit=" ms" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0B0F19', borderColor: '#334155', fontSize: '11px' }}
                />
                <Line
                  type="monotone"
                  dataKey="latency"
                  name="Simulated Network Latency (ms)"
                  stroke="#818CF8"
                  dot={false}
                  strokeWidth={2}
                  isAnimationActive={false}
                />
              </LineChart>
            )}
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
