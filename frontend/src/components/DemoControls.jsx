import React from 'react';
import { Play, PlusCircle, Zap, RefreshCw, AlertTriangle, ArrowRight } from 'lucide-react';

export default function DemoControls({
  systemState,
  onRunPlan,
  onAddZoneD,
  onReplan,
  onReset,
  isProcessing,
  onStartAutoDemo,
  demoStep
}) {
  const hasZoneD = systemState?.zones?.some(z => z.id === 'zone-d');
  const isPendingReplan = systemState?.is_pending_replan || hasZoneD;
  const hasPlan = Boolean(systemState?.current_plan);

  return (
    <div className="bg-slate-900/95 border border-slate-800 rounded-2xl p-5 shadow-2xl glass-card relative overflow-hidden font-sans">
      
      {/* Background Ambient Glow */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="flex flex-col lg:flex-row items-center justify-between gap-4 relative z-10">
        
        {/* Left Side Title & Status */}
        <div className="flex items-start gap-3">
          <div className="w-11 h-11 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center shrink-0">
            <Zap className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-white uppercase tracking-wide font-mono">
                Multi-Agent Response Controls
              </h2>
              {demoStep > 0 && (
                <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-cyan-500 text-slate-950 animate-pulse font-mono">
                  SIMULATION STEP {demoStep} / 5
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Simulate multi-agent negotiation, road network routing, fixed resource bounds, and dynamic re-planning.
            </p>
          </div>
        </div>

        {/* Action Buttons Group */}
        <div className="flex flex-wrap items-center gap-2.5 w-full lg:w-auto justify-end">
          
          {/* Start Response Simulation Button */}
          <button
            onClick={onStartAutoDemo}
            disabled={isProcessing}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-purple-500/25 transition-all duration-200 transform hover:-translate-y-0.5 disabled:opacity-50 cursor-pointer font-mono"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>[ ▶ START RESPONSE SIMULATION ]</span>
          </button>

          {/* Initial Plan Button */}
          {!hasPlan && (
            <button
              onClick={onRunPlan}
              disabled={isProcessing}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs shadow-lg shadow-cyan-600/25 transition-all duration-200 disabled:opacity-50 cursor-pointer font-mono"
            >
              <Zap className="w-4 h-4" />
              <span>CREATE RESPONSE PLAN</span>
            </button>
          )}

          {/* Add Zone D Button */}
          {!hasZoneD ? (
            <button
              onClick={onAddZoneD}
              disabled={isProcessing}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs shadow-lg shadow-amber-600/25 transition-all duration-200 disabled:opacity-50 cursor-pointer font-mono"
            >
              <PlusCircle className="w-4 h-4" />
              <span>[ + ADD NEW DISASTER ZONE ]</span>
            </button>
          ) : (
            <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-mono font-medium">
              <AlertTriangle className="w-4 h-4 text-amber-400 animate-bounce" />
              <span>ZONE D DETECTED</span>
            </div>
          )}

          {/* Re-plan Button */}
          {hasZoneD && (
            <button
              onClick={onReplan}
              disabled={isProcessing}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold text-xs shadow-xl shadow-red-600/30 transition-all duration-200 transform hover:scale-105 animate-pulse disabled:opacity-50 cursor-pointer font-mono"
            >
              <Zap className="w-4 h-4 fill-current" />
              <span>[ RE-PLAN RESPONSE ]</span>
            </button>
          )}

        </div>

      </div>

      {/* Dynamic Re-planning Alert Banner */}
      {hasZoneD && (
        <div className="mt-4 p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-between gap-3 text-xs text-amber-200 font-mono">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 animate-bounce" />
            <span>
              <strong>⚠️ NEW DISASTER ZONE DETECTED:</strong> Zone D (Hospital Landslide - 8 Critical, 20 Injured). Click <strong>[ RE-PLAN RESPONSE ]</strong> to trigger multi-agent re-allocation.
            </span>
          </div>
          <ArrowRight className="w-4 h-4 text-amber-400 animate-pulse shrink-0" />
        </div>
      )}

    </div>
  );
}
