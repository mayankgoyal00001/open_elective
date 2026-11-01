import React, { useRef, useEffect, useState, useCallback } from 'react';
import { ZoomIn, ZoomOut, Maximize2, Crosshair, Eye, ShieldAlert, Radio } from 'lucide-react';
import { VehicleState } from '../types/simulation';

interface RoadCanvasProps {
  vehicles: VehicleState[];
  isIntersection: boolean;
  selectedVehicleId: string | null;
  onSelectVehicle: (vehicleId: string) => void;
  communicationRange: number;
}

export const RoadCanvas: React.FC<RoadCanvasProps> = ({
  vehicles,
  isIntersection,
  selectedVehicleId,
  onSelectVehicle,
  communicationRange,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Viewport transforms (pan & zoom)
  const [scale, setScale] = useState<number>(1.0);
  const [offset, setOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [hoveredVehicle, setHoveredVehicle] = useState<VehicleState | null>(null);

  // Auto-fit initial view depending on highway or intersection
  const resetView = useCallback(() => {
    if (!containerRef.current) return;
    const { clientWidth, clientHeight } = containerRef.current;

    if (isIntersection) {
      // Center on intersection (300, 50)
      const baseScale = Math.min(clientWidth / 400, clientHeight / 300) * 0.9;
      setScale(baseScale);
      setOffset({
        x: clientWidth / 2 - 300 * baseScale,
        y: clientHeight / 2 - 50 * baseScale,
      });
    } else {
      // Highway road from 0 to 600m
      const baseScale = (clientWidth - 80) / 620;
      setScale(Math.max(1.1, baseScale));
      setOffset({
        x: 40,
        y: clientHeight / 2 - 26 * Math.max(1.1, baseScale),
      });
    }
  }, [isIntersection]);

  useEffect(() => {
    resetView();
  }, [isIntersection, resetView]);

  // Main Canvas Render Loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Handle high DPI display
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const width = rect.width;
    const height = rect.height;

    // Background fill (deep dark cockpit theme)
    ctx.fillStyle = '#070A10';
    ctx.fillRect(0, 0, width, height);

    // Apply pan & zoom transform
    ctx.save();
    ctx.translate(offset.x, offset.y);
    ctx.scale(scale, scale);

    // 1. Draw Road Geometry
    if (isIntersection) {
      drawIntersectionRoad(ctx);
    } else {
      drawHighwayRoad(ctx);
    }

    // 2. Draw V2V Communication Links
    drawCommunicationLinks(ctx, vehicles, communicationRange);

    // 3. Draw Selected Vehicle Halo
    if (selectedVehicleId) {
      const selected = vehicles.find((v) => v.vehicle_id === selectedVehicleId);
      if (selected) {
        drawRangeHalo(ctx, selected, communicationRange);
      }
    }

    // 4. Draw Collision Risk Vectors & Warnings
    drawCollisionThreatVectors(ctx, vehicles);

    // 5. Draw Vehicles
    vehicles.forEach((vehicle) => {
      drawVehicle(ctx, vehicle, vehicle.vehicle_id === selectedVehicleId);
    });

    ctx.restore();
  }, [vehicles, isIntersection, scale, offset, selectedVehicleId, communicationRange]);

  // Highway Renderer
  const drawHighwayRoad = (ctx: CanvasRenderingContext2D) => {
    const roadLength = 620;
    const roadTopY = 8;
    const laneHeight = 16;
    const numLanes = 2;
    const roadHeight = laneHeight * numLanes;

    // Roadbed asphalt
    ctx.fillStyle = '#0E1424';
    ctx.fillRect(0, roadTopY, roadLength, roadHeight);

    // Road borders / guardrails
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 2.5;
    ctx.strokeRect(0, roadTopY, roadLength, roadHeight);

    // Outer solid white road shoulder lines
    ctx.strokeStyle = '#94A3B8';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, roadTopY + 1);
    ctx.lineTo(roadLength, roadTopY + 1);
    ctx.moveTo(0, roadTopY + roadHeight - 1);
    ctx.lineTo(roadLength, roadTopY + roadHeight - 1);
    ctx.stroke();

    // Center dashed lane divider
    ctx.strokeStyle = '#F59E0B';
    ctx.lineWidth = 1.2;
    ctx.setLineDash([8, 8]);
    ctx.beginPath();
    ctx.moveTo(0, roadTopY + laneHeight);
    ctx.lineTo(roadLength, roadTopY + laneHeight);
    ctx.stroke();
    ctx.setLineDash([]);

    // Road distance ticks every 50 meters
    for (let x = 0; x <= roadLength; x += 50) {
      ctx.strokeStyle = '#1E293B';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x, roadTopY - 4);
      ctx.lineTo(x, roadTopY + roadHeight + 4);
      ctx.stroke();

      ctx.fillStyle = '#475569';
      ctx.font = '7px JetBrains Mono';
      ctx.fillText(`${x}m`, x - 6, roadTopY - 6);
    }

    // Lane labels
    ctx.fillStyle = '#334155';
    ctx.font = '8px Inter';
    ctx.fillText('LANE 0 (CRUISING)', 8, roadTopY + 7);
    ctx.fillText('LANE 1 (EXPRESS)', 8, roadTopY + laneHeight + 7);
  };

  // 4-Way Intersection Renderer
  const drawIntersectionRoad = (ctx: CanvasRenderingContext2D) => {
    const cx = 300;
    const cy = 50;
    const roadWidth = 32;

    // Background road corridors
    ctx.fillStyle = '#0E1424';
    // East-West road
    ctx.fillRect(50, cy - roadWidth / 2, 500, roadWidth);
    // North-South road
    ctx.fillRect(cx - roadWidth / 2, -180, roadWidth, 460);

    // Outer borders
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 2;
    // East-West borders
    ctx.strokeRect(50, cy - roadWidth / 2, 500, roadWidth);
    // North-South borders
    ctx.strokeRect(cx - roadWidth / 2, -180, roadWidth, 460);

    // Center conflict zone yellow crosshatch box
    const boxSize = roadWidth;
    ctx.fillStyle = '#1A2234';
    ctx.fillRect(cx - boxSize / 2, cy - boxSize / 2, boxSize, boxSize);

    ctx.strokeStyle = '#F59E0B';
    ctx.lineWidth = 1.2;
    ctx.strokeRect(cx - boxSize / 2, cy - boxSize / 2, boxSize, boxSize);

    // Crosshatch diagonals inside conflict zone
    ctx.strokeStyle = 'rgba(245, 158, 11, 0.35)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(cx - boxSize / 2, cy - boxSize / 2);
    ctx.lineTo(cx + boxSize / 2, cy + boxSize / 2);
    ctx.moveTo(cx + boxSize / 2, cy - boxSize / 2);
    ctx.lineTo(cx - boxSize / 2, cy + boxSize / 2);
    ctx.stroke();
    ctx.setLineDash([]);

    // Conflict zone text label
    ctx.fillStyle = '#F59E0B';
    ctx.font = 'bold 6px JetBrains Mono';
    ctx.fillText('CONFLICT ZONE', cx - 22, cy + 2);

    // White stop lines before conflict zone
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 2;
    // West approach stop line
    ctx.beginPath();
    ctx.moveTo(cx - boxSize / 2, cy - roadWidth / 2);
    ctx.lineTo(cx - boxSize / 2, cy + roadWidth / 2);
    // South approach stop line
    ctx.moveTo(cx - roadWidth / 2, cy - boxSize / 2);
    ctx.lineTo(cx + roadWidth / 2, cy - boxSize / 2);
    ctx.stroke();
  };

  // V2V Communication Link Lines
  const drawCommunicationLinks = (ctx: CanvasRenderingContext2D, vehs: VehicleState[], maxRange: number) => {
    ctx.save();
    for (let i = 0; i < vehs.length; i++) {
      for (let j = i + 1; j < vehs.length; j++) {
        const v1 = vehs[i];
        const v2 = vehs[j];
        const dist = Math.hypot(v1.x - v2.x, v1.y - v2.y);
        const effectiveRange = Math.min(v1.communication_range, maxRange);

        if (dist <= effectiveRange) {
          // Subtle cyan/blue connection line
          const opacity = Math.max(0.1, 0.45 * (1 - dist / effectiveRange));
          ctx.strokeStyle = `rgba(6, 182, 212, ${opacity})`;
          ctx.lineWidth = 1;
          ctx.setLineDash([3, 5]);

          ctx.beginPath();
          ctx.moveTo(v1.x, v1.y);
          ctx.lineTo(v2.x, v2.y);
          ctx.stroke();
        }
      }
    }
    ctx.restore();
  };

  // Communication Radius Halo
  const drawRangeHalo = (ctx: CanvasRenderingContext2D, v: VehicleState, maxRange: number) => {
    const range = Math.min(v.communication_range, maxRange);
    ctx.save();
    // Fill circle
    ctx.fillStyle = 'rgba(6, 182, 212, 0.05)';
    ctx.beginPath();
    ctx.arc(v.x, v.y, range, 0, Math.PI * 2);
    ctx.fill();

    // Border ring
    ctx.strokeStyle = 'rgba(6, 182, 212, 0.4)';
    ctx.lineWidth = 1.2;
    ctx.setLineDash([6, 6]);
    ctx.beginPath();
    ctx.arc(v.x, v.y, range, 0, Math.PI * 2);
    ctx.stroke();

    // Range text label
    ctx.fillStyle = '#06B6D4';
    ctx.font = '8px JetBrains Mono';
    ctx.fillText(`V2V Range: ${range.toFixed(0)}m`, v.x + range - 45, v.y - 4);
    ctx.restore();
  };

  // Collision Warning Threat Vectors
  const drawCollisionThreatVectors = (ctx: CanvasRenderingContext2D, vehs: VehicleState[]) => {
    ctx.save();
    vehs.forEach((v) => {
      if ((v.risk_level === 'CRITICAL' || v.risk_level === 'WARNING') && v.partner_vehicle_id) {
        const partner = vehs.find((p) => p.vehicle_id === v.partner_vehicle_id);
        if (partner) {
          const isCritical = v.risk_level === 'CRITICAL';
          const strokeColor = isCritical ? '#EF4444' : '#F59E0B';

          // Flashing threat trajectory line
          ctx.strokeStyle = strokeColor;
          ctx.lineWidth = isCritical ? 2.5 : 1.5;
          ctx.setLineDash([4, 3]);

          ctx.beginPath();
          ctx.moveTo(v.x, v.y);
          ctx.lineTo(partner.x, partner.y);
          ctx.stroke();
          ctx.setLineDash([]);

          // Midpoint threat label with TTC
          const midX = (v.x + partner.x) / 2;
          const midY = (v.y + partner.y) / 2 - 8;

          ctx.fillStyle = isCritical ? 'rgba(239, 68, 68, 0.9)' : 'rgba(245, 158, 11, 0.9)';
          const text = v.ttc_seconds !== null && v.ttc_seconds !== undefined
            ? `TTC: ${v.ttc_seconds}s`
            : 'COLLISION ALERT';

          ctx.font = 'bold 7px JetBrains Mono';
          const textWidth = ctx.measureText(text).width;
          ctx.fillRect(midX - textWidth / 2 - 3, midY - 7, textWidth + 6, 10);

          ctx.fillStyle = '#FFFFFF';
          ctx.fillText(text, midX - textWidth / 2, midY);
        }
      }
    });
    ctx.restore();
  };

  // Vehicle Car Marker Renderer
  const drawVehicle = (ctx: CanvasRenderingContext2D, v: VehicleState, isSelected: boolean) => {
    ctx.save();
    ctx.translate(v.x, v.y);
    ctx.rotate((v.heading * Math.PI) / 180);

    const length = v.dimensions.length_m || 4.8;
    const width = v.dimensions.width_m || 2.0;

    // Scale up slightly for crisp canvas readability (x3 visual magnification relative to road)
    const renderLength = length * 2.8;
    const renderWidth = width * 2.8;

    // If critical/warning, draw highlight glow
    if (v.risk_level === 'CRITICAL') {
      ctx.fillStyle = 'rgba(239, 68, 68, 0.35)';
      ctx.fillRect(-renderLength / 2 - 4, -renderWidth / 2 - 4, renderLength + 8, renderWidth + 8);
    } else if (v.risk_level === 'WARNING') {
      ctx.fillStyle = 'rgba(245, 158, 11, 0.25)';
      ctx.fillRect(-renderLength / 2 - 3, -renderWidth / 2 - 3, renderLength + 6, renderWidth + 6);
    }

    // Vehicle Selection Ring
    if (isSelected) {
      ctx.strokeStyle = '#06B6D4';
      ctx.lineWidth = 1.5;
      ctx.strokeRect(-renderLength / 2 - 3, -renderWidth / 2 - 3, renderLength + 6, renderWidth + 6);
    }

    // Vehicle Body Chassis
    ctx.fillStyle = v.color || '#3B82F6';
    ctx.beginPath();
    ctx.roundRect(-renderLength / 2, -renderWidth / 2, renderLength, renderWidth, 2.5);
    ctx.fill();

    // Vehicle Chassis Outline
    ctx.strokeStyle = isSelected ? '#FFFFFF' : '#0B0F19';
    ctx.lineWidth = 1;
    ctx.stroke();

    // Windshield (Front glass)
    ctx.fillStyle = '#070A10';
    ctx.fillRect(renderLength * 0.1, -renderWidth * 0.38, renderLength * 0.22, renderWidth * 0.76);

    // Rear window
    ctx.fillRect(-renderLength * 0.35, -renderWidth * 0.35, renderLength * 0.15, renderWidth * 0.7);

    // Front Headlights
    ctx.fillStyle = '#FEF08A';
    ctx.fillRect(renderLength / 2 - 1.5, -renderWidth / 2 + 0.8, 2, 2.2);
    ctx.fillRect(renderLength / 2 - 1.5, renderWidth / 2 - 3.0, 2, 2.2);

    // Rear Tail / Brake Lights
    if (v.emergency_braking || v.braking) {
      // Emergency Brake Flare Glow
      ctx.fillStyle = '#EF4444';
      ctx.shadowColor = '#EF4444';
      ctx.shadowBlur = 10;
      ctx.fillRect(-renderLength / 2 - 1.5, -renderWidth / 2 + 0.5, 2.5, 3);
      ctx.fillRect(-renderLength / 2 - 1.5, renderWidth / 2 - 3.5, 2.5, 3);
      ctx.shadowBlur = 0;
    } else {
      ctx.fillStyle = '#991B1B';
      ctx.fillRect(-renderLength / 2 - 0.5, -renderWidth / 2 + 0.8, 1.5, 2.2);
      ctx.fillRect(-renderLength / 2 - 0.5, renderWidth / 2 - 3.0, 1.5, 2.2);
    }

    ctx.restore();

    // Vehicle Roof Tags (render non-rotated for clean readability)
    ctx.save();
    ctx.translate(v.x, v.y);

    // ID Badge
    ctx.fillStyle = 'rgba(7, 10, 16, 0.85)';
    ctx.font = 'bold 7px JetBrains Mono';
    const idWidth = ctx.measureText(v.vehicle_id).width;
    ctx.fillRect(-idWidth / 2 - 2, -18, idWidth + 4, 9);

    ctx.fillStyle = isSelected ? '#38BDF8' : '#F1F5F9';
    ctx.fillText(v.vehicle_id, -idWidth / 2, -11);

    // Speed readout badge
    const speedText = `${Math.round(v.speed_kmh)} km/h`;
    ctx.font = '6px JetBrains Mono';
    const speedWidth = ctx.measureText(speedText).width;
    ctx.fillStyle = 'rgba(7, 10, 16, 0.85)';
    ctx.fillRect(-speedWidth / 2 - 2, 10, speedWidth + 4, 8);

    ctx.fillStyle = '#94A3B8';
    ctx.fillText(speedText, -speedWidth / 2, 16);

    ctx.restore();
  };

  // Mouse Interaction: Click to select vehicle
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Convert mouse pixels back to simulation coordinates
    const simX = (mouseX - offset.x) / scale;
    const simY = (mouseY - offset.y) / scale;

    // Find clicked vehicle within threshold
    const clicked = vehicles.find((v) => {
      const dist = Math.hypot(v.x - simX, v.y - simY);
      return dist <= 12; // 12 meters hit radius
    });

    if (clicked) {
      onSelectVehicle(clicked.vehicle_id);
    }
  };

  // Pan & Drag Handlers
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y });
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (isDragging) {
      setOffset({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }

    // Hover detection
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const simX = (mouseX - offset.x) / scale;
    const simY = (mouseY - offset.y) / scale;

    const hit = vehicles.find((v) => Math.hypot(v.x - simX, v.y - simY) <= 12);
    setHoveredVehicle(hit || null);
  };

  const handleMouseUp = () => setIsDragging(false);

  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.85;
    setScale((prev) => Math.min(4.0, Math.max(0.4, prev * zoomFactor)));
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full h-[400px] xl:h-[460px] bg-charcoal-950 border border-charcoal-800 rounded-xl overflow-hidden shadow-lg select-none"
    >
      {/* Simulation Scenario Overlay Tag */}
      <div className="absolute top-3 left-3 z-10 flex items-center gap-2 bg-charcoal-900/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-charcoal-700 text-xs font-mono">
        <Crosshair className="w-3.5 h-3.5 text-cyan-400" />
        <span className="text-slate-300 font-medium">
          {isIntersection ? '4-Way Intersection Grid (300m x 200m)' : 'Longitudinal Highway Corridor (600m)'}
        </span>
        <span className="text-slate-500">|</span>
        <span className="text-cyan-400">Scale: {(scale * 100).toFixed(0)}%</span>
      </div>

      {/* Floating Canvas Controls (Zoom In, Zoom Out, Reset Camera) */}
      <div className="absolute top-3 right-3 z-10 flex items-center gap-1 bg-charcoal-900/80 backdrop-blur-md p-1 rounded-lg border border-charcoal-700">
        <button
          onClick={() => setScale((prev) => Math.min(4.0, prev * 1.25))}
          title="Zoom In"
          className="p-1.5 rounded hover:bg-charcoal-700 text-slate-300 hover:text-white transition"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => setScale((prev) => Math.max(0.3, prev * 0.8))}
          title="Zoom Out"
          className="p-1.5 rounded hover:bg-charcoal-700 text-slate-300 hover:text-white transition"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={resetView}
          title="Reset Camera View"
          className="p-1.5 rounded hover:bg-charcoal-700 text-slate-300 hover:text-cyan-400 transition"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>

      {/* Hover Tooltip */}
      {hoveredVehicle && (
        <div className="absolute bottom-3 left-3 z-10 bg-charcoal-900/95 backdrop-blur-md border border-charcoal-700 px-3 py-2 rounded-lg text-xs font-mono text-slate-200 pointer-events-none shadow-xl flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: hoveredVehicle.color }} />
            <span className="font-bold text-white">{hoveredVehicle.vehicle_id}</span>
          </div>
          <div>Speed: <span className="text-cyan-400 font-semibold">{hoveredVehicle.speed_kmh} km/h</span></div>
          <div>Pos: <span className="text-slate-300">({hoveredVehicle.x.toFixed(1)}m, {hoveredVehicle.y.toFixed(1)}m)</span></div>
          <div>Risk: <span className={
            hoveredVehicle.risk_level === 'CRITICAL' ? 'text-rose-400 font-bold' :
            hoveredVehicle.risk_level === 'WARNING' ? 'text-amber-400 font-bold' : 'text-emerald-400'
          }>{hoveredVehicle.risk_level}</span></div>
        </div>
      )}

      {/* Canvas */}
      <canvas
        ref={canvasRef}
        onClick={handleCanvasClick}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        className={`w-full h-full block ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
      />
    </div>
  );
};
