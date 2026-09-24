import React from 'react';
import { AlertCircle, Users, HeartPulse, AlertTriangle, Navigation, Truck, Stethoscope, Home, Package, Trash2 } from 'lucide-react';

export default function ZoneCard({ zone, allocation, onDelete }) {
  const isCritical = zone.risk === 'Critical';
  const isHigh = zone.risk === 'High';

  const riskBadgeStyle = isCritical
    ? 'bg-red-500/20 text-red-300 border-red-500/40 animate-pulse'
    : isHigh
    ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
    : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';

  const cardBorderStyle = isCritical
    ? 'glass-card-glow-red'
    : zone.id === 'zone-d'
    ? 'border-amber-500/50 bg-slate-900/90 shadow-lg shadow-amber-500/10'
    : 'glass-card';

  return (
    <div className={`rounded-2xl p-5 border transition-all duration-300 relative overflow-hidden ${cardBorderStyle}`}>
      
      {/* Zone Header */}
      <div className="flex items-start justify-between gap-3 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-white font-mono">{zone.name}</h3>
            <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border uppercase ${riskBadgeStyle}`}>
              {zone.risk} Risk
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
            className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-red-400 hover:bg-slate-700 transition-colors"
            title="Remove Zone"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4 bg-slate-950/60 p-3 rounded-xl border border-slate-800 font-mono">
        <div className="flex flex-col">
          <span className="text-[10px] text-slate-400 uppercase flex items-center gap-1">
            <Users className="w-3 h-3 text-cyan-400" /> Pop
          </span>
          <span className="text-sm font-bold text-white mt-0.5">{zone.population}</span>
        </div>

        <div className="flex flex-col">
          <span className="text-[10px] text-slate-400 uppercase flex items-center gap-1">
            <HeartPulse className="w-3 h-3 text-rose-400" /> Injured
          </span>
          <span className="text-sm font-bold text-rose-300 mt-0.5">{zone.injured}</span>
        </div>

        <div className="flex flex-col">
          <span className="text-[10px] text-slate-400 uppercase flex items-center gap-1">
            <AlertTriangle className="w-3 h-3 text-red-500" /> Critical
          </span>
          <span className="text-sm font-bold text-red-400 mt-0.5">{zone.critical}</span>
        </div>

        <div className="flex flex-col">
          <span className="text-[10px] text-slate-400 uppercase flex items-center gap-1">
            <Navigation className="w-3 h-3 text-amber-400" /> Evac
          </span>
          <span className={`text-xs font-bold mt-0.5 ${zone.evacuation_required ? 'text-amber-400' : 'text-slate-400'}`}>
            {zone.evacuation_required ? 'REQUIRED' : 'No'}
          </span>
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
              <Home className="w-3.5 h-3.5 text-emerald-400 mx-auto mb-1" />
              <span className="text-xs font-bold text-white block">{allocation.shelter_units}</span>
              <span className="text-[9px] text-slate-400">Shelters</span>
            </div>

            <div className="bg-slate-800/80 p-2 rounded-lg border border-slate-700">
              <Package className="w-3.5 h-3.5 text-amber-400 mx-auto mb-1" />
              <span className="text-xs font-bold text-white block">{allocation.supplies}</span>
              <span className="text-[9px] text-slate-400">Supplies</span>
            </div>
          </div>

          {allocation.reason && (
            <p className="text-[11px] text-slate-400 italic mt-2 bg-slate-950/40 p-2 rounded border border-slate-800/80">
              "{allocation.reason}"
            </p>
          )}
        </div>
      ) : (
        <div className="pt-3 border-t border-slate-800 text-center text-xs text-slate-400 italic font-mono">
          Pending Multi-Agent Plan Generation...
        </div>
      )}

    </div>
  );
}
