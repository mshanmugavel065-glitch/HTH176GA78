import React from 'react';
import { Table, Truck, Stethoscope, Home, Package, AlertCircle, ArrowUpRight, ArrowDownRight, Layers } from 'lucide-react';

export default function ResponsePlan({ plan }) {
  if (!plan || !plan.final_allocations) {
    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-8 shadow-2xl glass-card text-center text-slate-400">
        <Layers className="w-10 h-10 text-slate-600 mx-auto mb-3" />
        <h4 className="text-base font-bold text-white font-mono">No Response Plan Generated Yet</h4>
        <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
          Execute the multi-agent pipeline using the controls above to synthesize validated allocations across all disaster zones.
        </p>
      </div>
    );
  }

  const allocations = plan.final_allocations;
  const changes = plan.changes || [];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl glass-card space-y-6">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Table className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
            Final Validated Disaster Response Plan
          </h3>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30">
          Generated at {plan.timestamp}
        </span>
      </div>

      {/* Re-planning Diff Banner (If changes exist) */}
      {changes.length > 0 && (
        <div className="bg-gradient-to-r from-purple-950/40 to-slate-900 border border-purple-500/40 rounded-xl p-4">
          <div className="flex items-center gap-2 text-xs font-bold text-purple-300 font-mono mb-2">
            <span className="w-2 h-2 rounded-full bg-purple-400 animate-ping" />
            DYNAMIC RE-PLANNING ADJUSTMENTS (BEFORE → AFTER)
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono">
            {changes.map((ch, idx) => (
              <div key={idx} className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="font-bold text-white">{ch.zone_name}:</span>{' '}
                  <span className="text-slate-400 uppercase">{ch.resource_type}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-400">{ch.before}</span>
                  <span className="text-purple-400">→</span>
                  <span className="text-emerald-400 font-bold bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/30">
                    {ch.after}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Allocations Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs font-mono">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-950/80 text-slate-400 uppercase tracking-wider">
              <th className="py-3 px-4">Zone</th>
              <th className="py-3 px-4">Priority</th>
              <th className="py-3 px-4 text-center">
                <span className="flex items-center justify-center gap-1">
                  <Truck className="w-3.5 h-3.5 text-cyan-400" /> Vehicles
                </span>
              </th>
              <th className="py-3 px-4 text-center">
                <span className="flex items-center justify-center gap-1">
                  <Stethoscope className="w-3.5 h-3.5 text-rose-400" /> Medics
                </span>
              </th>
              <th className="py-3 px-4 text-center">
                <span className="flex items-center justify-center gap-1">
                  <Home className="w-3.5 h-3.5 text-emerald-400" /> Shelters
                </span>
              </th>
              <th className="py-3 px-4 text-center">
                <span className="flex items-center justify-center gap-1">
                  <Package className="w-3.5 h-3.5 text-amber-400" /> Supplies
                </span>
              </th>
              <th className="py-3 px-4">Coordinator Rationale</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80">
            {allocations.map((alloc) => {
              const isCrit = alloc.priority === 'Critical';
              return (
                <tr
                  key={alloc.zone_id}
                  className={`hover:bg-slate-800/40 transition-colors ${
                    isCrit ? 'bg-red-950/10' : ''
                  }`}
                >
                  <td className="py-3 px-4 font-bold text-white">{alloc.zone_name}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border uppercase ${
                      isCrit
                        ? 'bg-red-500/20 text-red-300 border-red-500/40'
                        : alloc.priority === 'High'
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                        : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                    }`}>
                      {alloc.priority}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center font-bold text-cyan-300 text-sm">{alloc.vehicles}</td>
                  <td className="py-3 px-4 text-center font-bold text-rose-300 text-sm">{alloc.medics}</td>
                  <td className="py-3 px-4 text-center font-bold text-emerald-300 text-sm">{alloc.shelter_units}</td>
                  <td className="py-3 px-4 text-center font-bold text-amber-300 text-sm">{alloc.supplies}</td>
                  <td className="py-3 px-4 text-slate-300 text-[11px] max-w-xs truncate">
                    {alloc.reason || 'Optimal resource allocation.'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

    </div>
  );
}
