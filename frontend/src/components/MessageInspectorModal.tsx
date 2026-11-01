import React, { useState, useEffect } from 'react';
import { X, FileCode, Search, CheckCircle2, AlertOctagon, ArrowRight, RefreshCw } from 'lucide-react';
import { NetworkTransmissionLog } from '../types/simulation';
import { api } from '../services/api';

interface MessageInspectorModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MessageInspectorModal: React.FC<MessageInspectorModalProps> = ({ isOpen, onClose }) => {
  const [logs, setLogs] = useState<NetworkTransmissionLog[]>([]);
  const [selectedLog, setSelectedLog] = useState<NetworkTransmissionLog | null>(null);
  const [search, setSearch] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchLogs = async () => {
    try {
      const data = await api.fetchMessageLogs(60);
      setLogs(data);
      if (!selectedLog && data.length > 0) {
        setSelectedLog(data[data.length - 1]);
      }
    } catch (e) {
      // ignore
    }
  };

  useEffect(() => {
    if (!isOpen) return;
    fetchLogs();
    if (!autoRefresh) return;
    const interval = setInterval(fetchLogs, 1000);
    return () => clearInterval(interval);
  }, [isOpen, autoRefresh]);

  if (!isOpen) return null;

  const filteredLogs = logs.filter(
    (l) =>
      l.packet_id.toLowerCase().includes(search.toLowerCase()) ||
      l.sender_id.toLowerCase().includes(search.toLowerCase()) ||
      l.target_id.toLowerCase().includes(search.toLowerCase()) ||
      l.status.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-charcoal-900 border border-charcoal-750 rounded-2xl w-full max-w-5xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden font-mono">
        {/* Header */}
        <div className="p-4 border-b border-charcoal-800 bg-charcoal-850 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-cyan-950/80 border border-cyan-500/30 text-cyan-400">
              <FileCode className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-wide">
                V2V Basic Safety Message (BSM) Packet Inspector
              </h2>
              <p className="text-xs text-slate-400 font-sans">
                Cooperative Awareness message decode modeled after SAE J2735 and ETSI CAM specifications.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-2.5 py-1 rounded-lg text-xs border transition ${
                autoRefresh
                  ? 'bg-cyan-950 border-cyan-500/40 text-cyan-300'
                  : 'bg-charcoal-800 border-charcoal-700 text-slate-400'
              }`}
            >
              Auto-Stream: {autoRefresh ? 'ON' : 'PAUSED'}
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-charcoal-750 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Filter bar */}
        <div className="p-3 border-b border-charcoal-800 bg-charcoal-900 flex items-center gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search packet ID, vehicle node, or delivery status..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-charcoal-850 border border-charcoal-750 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>
          <button
            onClick={fetchLogs}
            className="p-2 rounded-lg bg-charcoal-850 border border-charcoal-750 hover:bg-charcoal-750 text-slate-300"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {/* Two-Pane Body: List on left, Decoded JSON on right */}
        <div className="flex-1 overflow-hidden grid grid-cols-1 md:grid-cols-12 divide-y md:divide-y-0 md:divide-x divide-charcoal-800 text-xs">
          {/* Packet Stream List (Left) */}
          <div className="md:col-span-6 overflow-y-auto p-3 space-y-1.5">
            {filteredLogs.length === 0 ? (
              <div className="p-8 text-center text-slate-500">No transmission logs match query.</div>
            ) : (
              [...filteredLogs].reverse().map((log) => {
                const isSelected = selectedLog?.packet_id === log.packet_id && selectedLog?.target_id === log.target_id;
                const isDropped = log.status.includes('DROPPED');
                return (
                  <div
                    key={`${log.packet_id}-${log.target_id}-${log.sent_at}`}
                    onClick={() => setSelectedLog(log)}
                    className={`p-2.5 rounded-lg border cursor-pointer transition ${
                      isSelected
                        ? 'bg-cyan-950/40 border-cyan-500/60 shadow-md'
                        : isDropped
                        ? 'bg-rose-950/20 border-rose-900/40 hover:border-rose-500/50'
                        : 'bg-charcoal-850 border-charcoal-750 hover:border-charcoal-600'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-slate-200">{log.packet_id}</span>
                      <span
                        className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                          isDropped
                            ? 'bg-rose-950 text-rose-400 border border-rose-500/40'
                            : 'bg-emerald-950 text-emerald-400 border border-emerald-500/40'
                        }`}
                      >
                        {log.status}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-slate-400 font-sans">
                      <div className="flex items-center gap-1.5 font-mono">
                        <span className="text-cyan-400 font-bold">{log.sender_id}</span>
                        <ArrowRight className="w-3 h-3 text-slate-600" />
                        <span className="text-slate-300 font-bold">{log.target_id}</span>
                      </div>
                      <div className="font-mono text-[10px]">
                        Dist: <span className="text-slate-200">{log.distance_m}m</span> | Lat: <span className="text-slate-200">{log.latency_ms}ms</span>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Decoded BSM Payload Inspector (Right) */}
          <div className="md:col-span-6 p-4 overflow-y-auto bg-charcoal-950">
            {selectedLog ? (
              <div>
                <div className="flex items-center justify-between pb-2 mb-3 border-b border-charcoal-800">
                  <span className="text-xs font-bold text-cyan-300">
                    Payload Decode: {selectedLog.packet_id}
                  </span>
                  <span className="text-[10px] text-slate-500">
                    Timestamp: {selectedLog.sent_at.toFixed(3)}s
                  </span>
                </div>

                <div className="space-y-3">
                  <div className="p-3 rounded-lg bg-charcoal-900 border border-charcoal-800 text-[11px]">
                    <div className="text-slate-400 mb-1 text-[10px] uppercase">Radio Propagation Telemetry</div>
                    <div className="grid grid-cols-2 gap-2 text-slate-300">
                      <div>Transmitter: <span className="text-cyan-400 font-bold">{selectedLog.sender_id}</span></div>
                      <div>Target: <span className="text-blue-400 font-bold">{selectedLog.target_id}</span></div>
                      <div>Clearance Distance: <span className="text-white">{selectedLog.distance_m} m</span></div>
                      <div>Simulated Queue Delay: <span className="text-indigo-400">{selectedLog.latency_ms} ms</span></div>
                      <div>Transport Status: <span className={selectedLog.status === 'DELIVERED' ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>{selectedLog.status}</span></div>
                    </div>
                  </div>

                  {/* Raw JSON Spec Dump */}
                  <div className="p-3 rounded-lg bg-charcoal-900 border border-charcoal-800 text-[11px]">
                    <div className="text-slate-400 mb-1.5 text-[10px] uppercase">
                      Raw SAE J2735 Cooperative Packet Frame
                    </div>
                    <pre className="text-slate-300 overflow-x-auto text-[11px] leading-relaxed p-2 bg-charcoal-950 rounded border border-charcoal-800">
{JSON.stringify(
  {
    header: {
      standard: "SAE_J2735_BSM",
      msg_id: selectedLog.packet_id,
      sim_timestamp: selectedLog.sent_at,
    },
    routing: {
      transmitter_id: selectedLog.sender_id,
      receiver_id: selectedLog.target_id,
      euclidean_range_m: selectedLog.distance_m,
      propagation_delay_ms: selectedLog.latency_ms,
      delivery_result: selectedLog.status
    },
    safety_payload: {
      hazard_light_active: false,
      electronic_emergency_brake_light: selectedLog.status === 'DELIVERED' ? true : false,
      data_integrity_check: "CRC32_VALID"
    }
  },
  null,
  2
)}
                    </pre>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500">
                Select a packet from the transmission stream to inspect payload
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
