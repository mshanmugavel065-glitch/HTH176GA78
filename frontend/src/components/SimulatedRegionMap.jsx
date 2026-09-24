import React from 'react';
import { Map, Navigation, AlertTriangle, CheckCircle2, ShieldAlert, Truck, Hospital, Home } from 'lucide-react';

export default function SimulatedRegionMap({ zones, allocations }) {
  const allocationsMap = {};
  if (allocations) {
    allocations.forEach(a => {
      allocationsMap[a.zone_id] = a;
    });
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Open':
        return { text: 'Road Open', style: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' };
      case 'Congested':
        return { text: 'Congested', style: 'bg-amber-500/20 text-amber-300 border-amber-500/40 font-bold' };
      case 'Blocked':
        return { text: 'BLOCKED', style: 'bg-red-500/20 text-red-400 border-red-500/50 font-extrabold animate-pulse' };
      default:
        return { text: status, style: 'bg-slate-800 text-slate-400 border-slate-700' };
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl glass-card">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Map className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
            Simulated Region Map & Road Network Status
          </h3>
        </div>
        <span className="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 px-2.5 py-0.5 rounded-full border border-cyan-500/30">
          Synthetic HTH-GA-07 Topology
        </span>
      </div>

      {/* Visual Map Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {zones?.map((zone) => {
          const alloc = allocationsMap[zone.id];
          const roadBadge = getStatusBadge(zone.road_status);
          const isBlocked = zone.road_status === 'Blocked';

          return (
            <div
              key={zone.id}
              className={`rounded-xl p-4 border transition-all relative overflow-hidden ${
                isBlocked
                  ? 'border-red-500/40 bg-red-950/20 shadow-lg shadow-red-500/10'
                  : 'border-slate-800 bg-slate-950/70'
              }`}
            >
              {/* Zone Title & Risk */}
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-white font-mono">{zone.name}</span>
                <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded border uppercase ${roadBadge.style}`}>
                  {roadBadge.text}
                </span>
              </div>

              {/* Population & Casualty Telemetry */}
              <div className="text-[11px] font-mono text-slate-300 space-y-1 my-3 bg-slate-900/90 p-2.5 rounded-lg border border-slate-800">
                <div className="flex justify-between">
                  <span className="text-slate-400">Population:</span>
                  <span className="font-bold text-white">{zone.population}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Casualties:</span>
                  <span className="font-bold text-rose-400">{zone.injured} Injured ({zone.critical} Crit)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Evacuation:</span>
                  <span className={`font-bold ${zone.evacuation_required ? 'text-amber-400' : 'text-slate-400'}`}>
                    {zone.evacuation_required ? 'REQUIRED' : 'No'}
                  </span>
                </div>
              </div>

              {/* Road Network & Routing details */}
              <div className="text-[10px] font-mono space-y-1">
                <div className="flex items-center gap-1 text-slate-300">
                  <Navigation className="w-3 h-3 text-cyan-400 shrink-0" />
                  <span className="truncate">{zone.road_name}</span>
                </div>
                {zone.alternate_route && (
                  <div className="text-emerald-400 font-bold flex items-center gap-1 bg-emerald-500/10 p-1.5 rounded border border-emerald-500/30 mt-1">
                    <CheckCircle2 className="w-3 h-3 shrink-0" />
                    <span className="truncate">Reroute: {zone.alternate_route}</span>
                  </div>
                )}
              </div>

              {/* Assigned Fleet Markers */}
              {alloc && (
                <div className="mt-3 pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] font-mono text-cyan-300">
                  <span>Assigned Fleet:</span>
                  <span className="font-bold flex items-center gap-1">
                    <Truck className="w-3 h-3 text-cyan-400" /> {alloc.vehicles} Veh | {alloc.medics} Med
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>

    </div>
  );
}
