import React, { useState, useEffect } from 'react';
import { X, Sliders, Check, RotateCcw, AlertTriangle } from 'lucide-react';
import { SimulationSettings } from '../types/simulation';
import { api } from '../services/api';

interface SimulationSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentSettings: SimulationSettings | null;
  onSettingsUpdated: () => void;
}

export const SimulationSettingsModal: React.FC<SimulationSettingsModalProps> = ({
  isOpen,
  onClose,
  currentSettings,
  onSettingsUpdated,
}) => {
  const [speedMultiplier, setSpeedMultiplier] = useState(1.0);
  const [vehicleCount, setVehicleCount] = useState(6);
  const [commRange, setCommRange] = useState(200);
  const [frequency, setFrequency] = useState(10);
  const [packetLoss, setPacketLoss] = useState(0);
  const [latency, setLatency] = useState(20);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (currentSettings) {
      setSpeedMultiplier(currentSettings.speed_multiplier);
      setVehicleCount(currentSettings.vehicle_count);
      setCommRange(currentSettings.communication_range_m);
      setFrequency(currentSettings.message_frequency_hz);
      setPacketLoss(currentSettings.packet_loss_percent);
      setLatency(currentSettings.network_latency_ms);
    }
  }, [currentSettings, isOpen]);

  if (!isOpen) return null;

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await api.updateSettings({
        speed_multiplier: speedMultiplier,
        vehicle_count: vehicleCount,
        communication_range_m: commRange,
        message_frequency_hz: frequency,
        packet_loss_percent: packetLoss,
        network_latency_ms: latency,
      });
      setSaveSuccess(true);
      onSettingsUpdated();
      setTimeout(() => {
        setSaveSuccess(false);
        onClose();
      }, 600);
    } catch (e) {
      alert('Failed to update simulation settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleResetDefaults = () => {
    setSpeedMultiplier(1.0);
    setVehicleCount(6);
    setCommRange(200);
    setFrequency(10);
    setPacketLoss(0);
    setLatency(20);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-charcoal-900 border border-charcoal-750 rounded-2xl w-full max-w-xl flex flex-col shadow-2xl overflow-hidden font-mono">
        {/* Header */}
        <div className="p-4 border-b border-charcoal-800 bg-charcoal-850 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-indigo-950/80 border border-indigo-500/30 text-indigo-400">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-wide">
                Simulation & Network Configuration
              </h2>
              <p className="text-xs text-slate-400 font-sans">
                Real-time adjustment of physical speed, wireless parameters, and vehicle density.
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

        {/* Sliders Form */}
        <div className="p-5 space-y-5 text-xs">
          {/* Speed Multiplier */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-300 font-medium">Physics Speed Factor</span>
              <span className="text-cyan-400 font-bold">{speedMultiplier.toFixed(1)}x</span>
            </div>
            <div className="flex items-center gap-2">
              {[0.5, 1.0, 2.0, 3.0, 5.0].map((val) => (
                <button
                  key={val}
                  type="button"
                  onClick={() => setSpeedMultiplier(val)}
                  className={`flex-1 py-1 rounded border text-center transition ${
                    speedMultiplier === val
                      ? 'bg-cyan-500 text-black font-bold border-cyan-400'
                      : 'bg-charcoal-850 border-charcoal-700 text-slate-400 hover:text-white'
                  }`}
                >
                  {val}x
                </button>
              ))}
            </div>
          </div>

          {/* Vehicle Count */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-300 font-medium">Simulated Vehicle Density</span>
              <span className="text-blue-400 font-bold">{vehicleCount} vehicles</span>
            </div>
            <input
              type="range"
              min="2"
              max="12"
              step="1"
              value={vehicleCount}
              onChange={(e) => setVehicleCount(parseInt(e.target.value))}
              className="w-full accent-blue-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>2 (Minimal)</span>
              <span>6 (Default)</span>
              <span>12 (Heavy)</span>
            </div>
          </div>

          {/* Communication Range */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-300 font-medium">V2V Wireless Range (Radius)</span>
              <span className="text-cyan-400 font-bold">{commRange} meters</span>
            </div>
            <input
              type="range"
              min="50"
              max="500"
              step="25"
              value={commRange}
              onChange={(e) => setCommRange(parseInt(e.target.value))}
              className="w-full accent-cyan-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>50m (Short)</span>
              <span>200m (Standard DSRC)</span>
              <span>500m (Long)</span>
            </div>
          </div>

          {/* BSM Message Frequency */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-300 font-medium">BSM Broadcast Rate</span>
              <span className="text-indigo-400 font-bold">{frequency} Hz</span>
            </div>
            <input
              type="range"
              min="1"
              max="20"
              step="1"
              value={frequency}
              onChange={(e) => setFrequency(parseInt(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>1 Hz</span>
              <span>10 Hz (SAE J2735)</span>
              <span>20 Hz</span>
            </div>
          </div>

          {/* Packet Loss % */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-300 font-medium">RF Interference / Packet Loss</span>
              <span className={`font-bold ${packetLoss > 20 ? 'text-rose-400' : 'text-slate-300'}`}>
                {packetLoss}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="80"
              step="5"
              value={packetLoss}
              onChange={(e) => setPacketLoss(parseInt(e.target.value))}
              className="w-full accent-rose-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>0% (Ideal)</span>
              <span>30% (Faded)</span>
              <span>80% (Severe Failure)</span>
            </div>
          </div>

          {/* Network Latency ms */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-300 font-medium">Simulated Network Propagation Latency</span>
              <span className="text-amber-400 font-bold">{latency} ms</span>
            </div>
            <input
              type="range"
              min="0"
              max="400"
              step="10"
              value={latency}
              onChange={(e) => setLatency(parseInt(e.target.value))}
              className="w-full accent-amber-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>0 ms (Instant)</span>
              <span>20 ms (Nominal)</span>
              <span>400 ms (Degraded)</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-charcoal-800 bg-charcoal-850 flex items-center justify-between">
          <button
            type="button"
            onClick={handleResetDefaults}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-slate-400 hover:text-white bg-charcoal-800 hover:bg-charcoal-750 transition text-xs"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Defaults
          </button>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-white bg-transparent transition text-xs"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-bold transition text-xs shadow-md shadow-cyan-950"
            >
              {saveSuccess ? (
                <>
                  <Check className="w-4 h-4" /> Applied!
                </>
              ) : (
                'Apply Settings'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
