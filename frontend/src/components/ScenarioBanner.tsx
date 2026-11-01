import React from 'react';
import { Layers, CheckCircle, ArrowRight, Play, RotateCcw, AlertTriangle } from 'lucide-react';
import { ScenarioInfo } from '../types/simulation';

interface ScenarioBannerProps {
  currentScenario: ScenarioInfo | null;
  scenarios: ScenarioInfo[];
  onSelectScenario: (id: string) => void;
  onReset: () => void;
  onStart: () => void;
  isRunning: boolean;
}

export const ScenarioBanner: React.FC<ScenarioBannerProps> = ({
  currentScenario,
  scenarios,
  onSelectScenario,
  onReset,
  onStart,
  isRunning,
}) => {
  if (!currentScenario) return null;

  return (
    <div className="bg-charcoal-900 border border-charcoal-800 rounded-xl p-4 shadow-md font-mono text-xs">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Scenario Details */}
        <div className="space-y-1.5 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-500/40 text-cyan-300 font-bold uppercase tracking-wider">
              {currentScenario.category}
            </span>
            <h3 className="text-sm font-bold text-white tracking-wide">
              {currentScenario.name}
            </h3>
          </div>

          <p className="text-slate-300 text-xs font-sans leading-relaxed">
            {currentScenario.description}
          </p>

          <div className="flex items-start gap-1.5 text-[11px] text-emerald-400 font-sans pt-1">
            <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <span>
              <strong className="font-semibold text-emerald-300">Expected Automotive Outcome:</strong>{' '}
              {currentScenario.expected_outcome}
            </span>
          </div>
        </div>

        {/* Quick Scenario Switcher Chips & Run Action */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 shrink-0">
          <div className="flex flex-wrap items-center gap-1.5">
            {scenarios.map((sc) => (
              <button
                key={sc.id}
                onClick={() => onSelectScenario(sc.id)}
                className={`px-2.5 py-1.5 rounded-lg text-[11px] font-semibold border transition ${
                  currentScenario.id === sc.id
                    ? 'bg-blue-600/30 border-blue-500 text-cyan-300 shadow-sm'
                    : 'bg-charcoal-850 border-charcoal-750 text-slate-400 hover:text-white hover:border-charcoal-600'
                }`}
              >
                {sc.id.split('_')[0].toUpperCase()}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-1.5 pl-2 sm:border-l border-charcoal-750">
            <button
              onClick={onStart}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition shadow-sm"
            >
              <Play className="w-3.5 h-3.5 fill-white" />
              <span>{isRunning ? 'Restart' : 'Run'}</span>
            </button>
            <button
              onClick={onReset}
              title="Reset initial scenario state"
              className="p-1.5 rounded-lg bg-charcoal-850 border border-charcoal-750 hover:bg-charcoal-750 text-slate-300 hover:text-white transition"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
