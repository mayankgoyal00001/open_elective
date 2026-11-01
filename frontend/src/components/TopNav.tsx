import React from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Radio, 
  Activity, 
  Sliders, 
  Layers, 
  Wifi, 
  WifiOff, 
  ShieldAlert,
  FileCode
} from 'lucide-react';
import { ScenarioInfo, SimulationSnapshot } from '../types/simulation';

interface TopNavProps {
  snapshot: SimulationSnapshot | null;
  isConnected: boolean;
  scenarios: ScenarioInfo[];
  onPlay: () => void;
  onPause: () => void;
  onReset: () => void;
  onSelectScenario: (id: string) => void;
  onOpenSettings: () => void;
  onOpenAnalytics: () => void;
  onOpenInspector: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({
  snapshot,
  isConnected,
  scenarios,
  onPlay,
  onPause,
  onReset,
  onSelectScenario,
  onOpenSettings,
  onOpenAnalytics,
  onOpenInspector,
}) => {
  const status = snapshot?.status || 'STOPPED';
  const simTime = snapshot?.sim_time ?? 0;
  const currentScenario = snapshot?.scenario_id || 'normal_traffic';

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    const ms = Math.floor((secs % 1) * 100);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
  };

  return (
    <header className="border-b border-charcoal-700 bg-charcoal-900/90 backdrop-blur-md sticky top-0 z-40 px-4 py-2.5">
      <div className="max-w-[1700px] mx-auto flex flex-wrap items-center justify-between gap-3">
        {/* Brand & Project Identity */}
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.25)]">
            <Radio className="w-5 h-5 animate-pulse" />
            <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
            </span>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold tracking-wider font-mono bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-300 bg-clip-text text-transparent">
                SmartV2V
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-blue-950/80 border border-blue-500/40 text-blue-300 font-semibold tracking-wide uppercase">
                SDV Engine
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">
              Vehicle-to-Vehicle Safety & Collision Avoidance Platform
            </p>
          </div>

          {/* Mandatory College Requirement Badge */}
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-950/50 border border-amber-600/40 text-amber-300 text-[11px] font-medium tracking-tight">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
            <span>SOFTWARE SIMULATION — NO PHYSICAL VEHICLES CONNECTED</span>
          </div>
        </div>

        {/* Center: Scenario Selector & Sim Time */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-charcoal-850 px-3 py-1.5 rounded-lg border border-charcoal-700">
            <Layers className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={currentScenario}
              onChange={(e) => onSelectScenario(e.target.value)}
              className="bg-transparent text-xs font-medium text-slate-200 focus:outline-none cursor-pointer pr-1"
            >
              {scenarios.map((sc) => (
                <option key={sc.id} value={sc.id} className="bg-charcoal-900 text-slate-200">
                  {sc.name}
                </option>
              ))}
            </select>
          </div>

          {/* Sim Time Clock */}
          <div className="flex items-center gap-2 bg-charcoal-850 px-3 py-1.5 rounded-lg border border-charcoal-700 font-mono text-xs">
            <span className="text-slate-400 text-[10px] uppercase tracking-wider">Sim Time</span>
            <span className="text-cyan-400 font-bold tracking-wider">{formatTime(simTime)}</span>
          </div>
        </div>

        {/* Right: Controls & Action Modals */}
        <div className="flex items-center gap-2">
          {/* Status Pill */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono font-medium border border-charcoal-700 bg-charcoal-850">
            <span
              className={`w-2 h-2 rounded-full ${
                status === 'RUNNING' ? 'bg-emerald-400 animate-pulse' : status === 'PAUSED' ? 'bg-amber-400' : 'bg-rose-500'
              }`}
            />
            <span className={status === 'RUNNING' ? 'text-emerald-400' : status === 'PAUSED' ? 'text-amber-400' : 'text-slate-400'}>
              {status}
            </span>
          </div>

          {/* Connection Pill */}
          <div className="flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-mono border border-charcoal-700 bg-charcoal-850">
            {isConnected ? (
              <span className="flex items-center gap-1 text-emerald-400 text-[11px]">
                <Wifi className="w-3.5 h-3.5" /> Live WS
              </span>
            ) : (
              <span className="flex items-center gap-1 text-rose-400 text-[11px]">
                <WifiOff className="w-3.5 h-3.5" /> Disconnected
              </span>
            )}
          </div>

          {/* Controls: Play/Pause/Reset */}
          <div className="flex items-center gap-1 bg-charcoal-850 p-1 rounded-lg border border-charcoal-700">
            {status === 'RUNNING' ? (
              <button
                onClick={onPause}
                title="Pause Simulation"
                className="p-1.5 rounded hover:bg-amber-500/20 text-amber-400 transition"
              >
                <Pause className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={onPlay}
                title="Start / Resume Simulation"
                className="p-1.5 rounded hover:bg-emerald-500/20 text-emerald-400 transition"
              >
                <Play className="w-4 h-4 fill-emerald-400/30" />
              </button>
            )}

            <button
              onClick={onReset}
              title="Reset Simulation Scenario"
              className="p-1.5 rounded hover:bg-charcoal-700 text-slate-300 hover:text-white transition"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>

          {/* Action Modals */}
          <div className="flex items-center gap-1.5 pl-2 border-l border-charcoal-700">
            <button
              onClick={onOpenInspector}
              title="Inspect Raw V2V BSM Packets"
              className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-lg bg-charcoal-850 hover:bg-charcoal-800 text-slate-300 hover:text-cyan-300 border border-charcoal-700 transition"
            >
              <FileCode className="w-3.5 h-3.5 text-cyan-400" />
              <span className="hidden xl:inline">BSM Inspector</span>
            </button>

            <button
              onClick={onOpenAnalytics}
              title="Network & Wireless Analytics"
              className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-lg bg-charcoal-850 hover:bg-charcoal-800 text-slate-300 hover:text-blue-300 border border-charcoal-700 transition"
            >
              <Activity className="w-3.5 h-3.5 text-blue-400" />
              <span className="hidden xl:inline">Network Analytics</span>
            </button>

            <button
              onClick={onOpenSettings}
              title="Simulation & Safety Thresholds"
              className="p-1.5 text-xs rounded-lg bg-charcoal-850 hover:bg-charcoal-800 text-slate-300 hover:text-white border border-charcoal-700 transition"
            >
              <Sliders className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
