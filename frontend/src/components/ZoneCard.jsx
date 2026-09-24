import React from 'react';
import { CloudRain, Waves, Users, HeartPulse, AlertTriangle, Navigation, Truck, Stethoscope, Home, Package, Trash2, ShieldAlert } from 'lucide-react';

export default function ZoneCard({ zone, allocation, onDelete }) {
  const riskLevel = zone.risk_level || zone.risk || 'Moderate';
  const isCritical = riskLevel.toLowerCase() === 'critical';
  const isVeryHigh = riskLevel.toLowerCase() === 'very high';
  const isHigh = riskLevel.toLowerCase() === 'high';

  const riskBadgeStyle = isCritical
    ? 'bg-rose-500/20 text-rose-300 border-rose-500/50 animate-pulse'
    : isVeryHigh
    ? 'bg-orange-500/20 text-orange-300 border-orange-500/50'
    : isHigh
    ? 'bg-amber-500/20 text-amber-300 border-amber-500/50'
    : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50';

  const cardBorderStyle = isCritical
    ? 'glass-card-glow-red border-rose-500/40'
    : zone.id === 'zone-d'
    ? 'border-amber-500/50 bg-slate-900/90 shadow-lg shadow-amber-500/10'
    : 'glass-card';

  const severityScore = zone.severity_score || 0.0;

  return (
    <div className={`rounded-2xl p-5 border transition-all duration-300 relative overflow-hidden flex flex-col justify-between ${cardBorderStyle}`}>
      
      <div>
        {/* Zone Header */}
        <div className="flex items-start justify-between gap-2 mb-3">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-base font-bold text-white font-mono">{zone.name}</h3>
              <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border uppercase ${riskBadgeStyle}`}>
                {riskLevel}
              </span>
            </div>
            {zone.description && (
              <p className="text-xs text-slate-400 mt-1 line-clamp-2">{zone.description}</p>
            )}
          </div>

          {/* Delete Zone Button (if custom/Zone D) */}
          {zone.id === 'zone-d' && onDelete && (
            <button
              onClick={() => onDelete(zone.id)}
              className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-rose-400 hover:bg-slate-700 transition-colors cursor-pointer"
              title="Remove Sector"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Hazard Metrics Banner (Rainfall, Flood Level, Severity Score) */}
        <div className="grid grid-cols-3 gap-2 mb-3 bg-slate-950/80 p-2.5 rounded-xl border border-slate-800/80 font-mono text-center">
          <div className="flex flex-col">
            <span className="text-[9px] text-slate-400 uppercase flex items-center justify-center gap-1">
              <CloudRain className="w-3 h-3 text-cyan-400" /> Rain
            </span>
            <span className="text-xs font-bold text-cyan-300 mt-0.5">{zone.rainfall_mm || 0}mm</span>
          </div>

          <div className="flex flex-col">
            <span className="text-[9px] text-slate-400 uppercase flex items-center justify-center gap-1">
              <Waves className="w-3 h-3 text-blue-400" /> Flood
            </span>
            <span className="text-xs font-bold text-blue-300 mt-0.5">{zone.flood_level_m || 0}m</span>
          </div>

          <div className="flex flex-col">
            <span className="text-[9px] text-slate-400 uppercase flex items-center justify-center gap-1">
              <ShieldAlert className="w-3 h-3 text-purple-400" /> Score
            </span>
            <span className="text-xs font-bold text-purple-300 mt-0.5">{severityScore}/100</span>
          </div>
        </div>

        {/* Secondary Metrics Grid */}
        <div className="grid grid-cols-4 gap-1.5 mb-4 bg-slate-950/40 p-2.5 rounded-xl border border-slate-800 font-mono">
          <div className="flex flex-col">
            <span className="text-[9px] text-slate-400 uppercase flex items-center gap-0.5">
              <Users className="w-2.5 h-2.5 text-slate-400" /> Pop
            </span>
            <span className="text-xs font-bold text-slate-200 mt-0.5">{zone.population}</span>
          </div>

          <div className="flex flex-col">
            <span className="text-[9px] text-slate-400 uppercase flex items-center gap-0.5">
              <HeartPulse className="w-2.5 h-2.5 text-rose-400" /> Injured
            </span>
            <span className="text-xs font-bold text-rose-300 mt-0.5">{zone.injured}</span>
          </div>

          <div className="flex flex-col">
            <span className="text-[9px] text-slate-400 uppercase flex items-center gap-0.5">
              <AlertTriangle className="w-2.5 h-2.5 text-rose-500" /> Crit
            </span>
            <span className="text-xs font-bold text-rose-400 mt-0.5">{zone.critical}</span>
          </div>

          <div className="flex flex-col">
            <span className="text-[9px] text-slate-400 uppercase flex items-center gap-0.5">
              <Navigation className="w-2.5 h-2.5 text-amber-400" /> Evac
            </span>
            <span className={`text-[11px] font-bold mt-0.5 ${zone.evacuation_required ? 'text-amber-400' : 'text-slate-400'}`}>
              {zone.evacuation_required ? 'YES' : 'NO'}
            </span>
          </div>
        </div>
      </div>

      {/* Allocated Resources Banner */}
      {allocation ? (
        <div className="pt-3 border-t border-slate-800">
          <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider font-semibold block mb-2">
            AI Assigned Resources:
          </span>
          <div className="grid grid-cols-4 gap-1.5 text-center font-mono">
            <div className="bg-slate-800/80 p-2 rounded-lg border border-slate-700">
              <Truck className="w-3.5 h-3.5 text-cyan-400 mx-auto mb-1" />
              <span className="text-xs font-bold text-white block">{allocation.vehicles}</span>
              <span className="text-[9px] text-slate-400">Vehicles</span>
            </div>

            <div className="bg-slate-800/80 p-2 rounded-lg border border-slate-700">
              <Stethoscope className="w-3.5 h-3.5 text-rose-400 mx-auto mb-1" />
              <span className="text-xs font-bold text-white block">{allocation.medics}</span>
              <span className="text-[9px] text-slate-400">Medics</span>
            </div>

            <div className="bg-slate-800/80 p-2 rounded-lg border border-slate-700">
              <Home className="w-3.5 h-3.5 text-purple-400 mx-auto mb-1" />
              <span className="text-xs font-bold text-white block">{allocation.shelter_units}</span>
              <span className="text-[9px] text-slate-400">Shelters</span>
            </div>

            <div className="bg-slate-800/80 p-2 rounded-lg border border-slate-700">
              <Package className="w-3.5 h-3.5 text-emerald-400 mx-auto mb-1" />
              <span className="text-xs font-bold text-white block">{allocation.supplies}</span>
              <span className="text-[9px] text-slate-400">Supplies</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="pt-3 border-t border-slate-800 text-center">
          <span className="text-xs font-mono text-slate-500 italic">No resources allocated yet</span>
        </div>
      )}

    </div>
  );
}
