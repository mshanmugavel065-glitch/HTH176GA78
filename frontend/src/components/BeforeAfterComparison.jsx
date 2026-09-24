import React from 'react';
import { ArrowRight, RefreshCw, AlertCircle, Info, Sparkles } from 'lucide-react';

export default function BeforeAfterComparison({ previousPlan, currentPlan, differences }) {
  if (!previousPlan || !currentPlan || (!differences || differences.length === 0)) {
    return null;
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
      
      {/* Title Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <RefreshCw className="w-5 h-5 text-cyan-400" />
          <h3 className="text-base font-bold text-white uppercase tracking-wider font-mono">
            DYNAMIC RE-PLANNING DIFFERENTIAL (BEFORE vs AFTER)
          </h3>
        </div>
        <span className="px-2.5 py-1 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-mono font-semibold">
          {differences.length} Re-allocation Shifts
        </span>
      </div>

      {/* BEFORE / AFTER Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* BEFORE Card */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
            <span className="text-xs font-bold text-slate-400 uppercase font-mono tracking-wider">
              BEFORE (Previous Baseline)
            </span>
            <span className="text-[11px] text-slate-500 font-mono">{previousPlan.timestamp}</span>
          </div>

          <div className="space-y-2">
            {previousPlan.final_allocations?.map((alloc) => (
              <div key={alloc.zone_id} className="flex items-center justify-between text-xs font-mono bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/60">
                <span className="font-semibold text-slate-300">{alloc.zone_name}</span>
                <div className="flex items-center gap-2 text-slate-400 text-[11px]">
                  <span>Priority: <strong className="text-amber-400">{alloc.priority}</strong></span>
                  <span>🚑 {alloc.vehicles}</span>
                  <span>🏥 {alloc.medics}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AFTER Card */}
        <div className="bg-slate-950/60 border border-cyan-500/30 rounded-xl p-4 space-y-3 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/10 rounded-full blur-xl pointer-events-none" />

          <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
            <span className="text-xs font-bold text-cyan-300 uppercase font-mono tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              AFTER (Updated Dynamic Response Plan)
            </span>
            <span className="text-[11px] text-cyan-400 font-mono font-semibold">{currentPlan.timestamp}</span>
          </div>

          <div className="space-y-2">
            {currentPlan.final_allocations?.map((alloc) => (
              <div key={alloc.zone_id} className="flex items-center justify-between text-xs font-mono bg-slate-900/90 p-2.5 rounded-lg border border-cyan-500/20">
                <span className="font-semibold text-white">{alloc.zone_name}</span>
                <div className="flex items-center gap-2 text-slate-300 text-[11px]">
                  <span>Priority: <strong className="text-rose-400">{alloc.priority}</strong></span>
                  <span className="text-cyan-300 font-bold">🚑 {alloc.vehicles}</span>
                  <span className="text-purple-300 font-bold">🏥 {alloc.medics}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* WHAT CHANGED & WHY Section */}
      <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 space-y-3 font-mono text-xs">
        <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
          <Info className="w-4 h-4 text-cyan-400" />
          WHAT CHANGED & WHY?
        </h4>

        <div className="space-y-2 pt-1">
          {differences.map((diff) => (
            <div key={diff.zone_id} className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1">
              <div className="flex items-center justify-between font-semibold text-cyan-300 text-xs">
                <span>{diff.zone_name} Resource Shift</span>
                <span className="text-slate-400 text-[11px]">
                  Vehicles: ({diff.before_vehicles} → <strong className="text-cyan-400">{diff.after_vehicles}</strong>) | 
                  Medics: ({diff.before_medics} → <strong className="text-purple-400">{diff.after_medics}</strong>)
                </span>
              </div>
              <p className="text-[11px] text-slate-300 font-sans">
                <strong className="text-slate-400">Reason:</strong> {diff.reason}
              </p>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
