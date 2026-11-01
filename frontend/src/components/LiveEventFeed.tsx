import React, { useState, useRef, useEffect } from 'react';
import { ShieldAlert, AlertTriangle, Info, Bell, Trash2, Filter } from 'lucide-react';
import { SafetyEvent } from '../types/simulation';

interface LiveEventFeedProps {
  events: SafetyEvent[];
  onSelectVehicle?: (vehicleId: string) => void;
}

export const LiveEventFeed: React.FC<LiveEventFeedProps> = ({ events, onSelectVehicle }) => {
  const [filter, setFilter] = useState<'ALL' | 'CRITICAL' | 'WARNING' | 'INFO'>('ALL');
  const scrollRef = useRef<HTMLDivElement | null>(null);

  const filteredEvents = events.filter((e) => {
    if (filter === 'ALL') return true;
    return e.severity === filter;
  });

  // Auto-scroll to top when new events arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [events.length]);

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950/80 text-rose-400 border border-rose-500/40">
            <ShieldAlert className="w-3 h-3" /> CRITICAL
          </span>
        );
      case 'WARNING':
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950/80 text-amber-400 border border-amber-500/40">
            <AlertTriangle className="w-3 h-3" /> WARNING
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium bg-blue-950/80 text-blue-400 border border-blue-500/40">
            <Info className="w-3 h-3" /> INFO
          </span>
        );
    }
  };

  return (
    <div className="bg-charcoal-900 border border-charcoal-800 rounded-xl flex flex-col h-[400px] xl:h-[460px] overflow-hidden shadow-lg">
      {/* Header & Severity Filters */}
      <div className="p-3 border-b border-charcoal-800 bg-charcoal-850/80 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-semibold text-slate-200 tracking-wide uppercase">
            Live Safety Event Feed
          </span>
          <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-charcoal-700 text-slate-300 font-mono">
            {events.length}
          </span>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1 bg-charcoal-900 p-0.5 rounded-lg border border-charcoal-700 text-[10px] font-mono">
          {(['ALL', 'CRITICAL', 'WARNING', 'INFO'] as const).map((lvl) => (
            <button
              key={lvl}
              onClick={() => setFilter(lvl)}
              className={`px-2 py-0.5 rounded transition ${
                filter === lvl
                  ? 'bg-charcoal-700 text-white font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>
      </div>

      {/* Events Scroll Area (newest on top) */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-2">
        {filteredEvents.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 text-xs py-8">
            <Info className="w-6 h-6 mb-2 opacity-40 text-slate-400" />
            <span>No events recorded for current filter</span>
          </div>
        ) : (
          [...filteredEvents].reverse().map((evt) => (
            <div
              key={evt.event_id}
              className={`p-2.5 rounded-lg border text-xs font-mono transition ${
                evt.severity === 'CRITICAL'
                  ? 'bg-rose-950/20 border-rose-500/40 hover:border-rose-500'
                  : evt.severity === 'WARNING'
                  ? 'bg-amber-950/20 border-amber-500/40 hover:border-amber-500'
                  : 'bg-charcoal-850/80 border-charcoal-750 hover:border-cyan-500/40'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-1">
                <div className="flex items-center gap-2">
                  {getSeverityBadge(evt.severity)}
                  <span className="text-[10px] text-slate-400 font-medium">
                    {evt.event_type}
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">
                  {evt.timestamp.toFixed(2)}s
                </span>
              </div>

              <p className="text-slate-200 text-[11px] leading-relaxed my-1 font-sans">
                {evt.description}
              </p>

              {/* Subject Vehicle Badges & Telemetry */}
              <div className="flex items-center justify-between text-[10px] pt-1 border-t border-charcoal-750/50 mt-1">
                <div className="flex items-center gap-1.5">
                  <span className="text-slate-500">Node:</span>
                  <button
                    onClick={() => onSelectVehicle && onSelectVehicle(evt.primary_vehicle_id)}
                    className="text-cyan-400 hover:underline font-bold"
                  >
                    {evt.primary_vehicle_id}
                  </button>
                  {evt.secondary_vehicle_id && (
                    <>
                      <span className="text-slate-600">↔</span>
                      <button
                        onClick={() => onSelectVehicle && onSelectVehicle(evt.secondary_vehicle_id!)}
                        className="text-slate-300 hover:underline font-bold"
                      >
                        {evt.secondary_vehicle_id}
                      </button>
                    </>
                  )}
                </div>

                {evt.ttc_seconds !== null && evt.ttc_seconds !== undefined && (
                  <div className="text-amber-400 font-semibold">
                    TTC: {evt.ttc_seconds}s
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
