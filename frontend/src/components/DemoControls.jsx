import React from 'react';
import { Play, PlusCircle, Zap, RefreshCw, AlertTriangle, CloudRain } from 'lucide-react';
import DatasetUpload from './DatasetUpload';

export default function DemoControls({
  systemState,
  onRunPlan,
  onAddZoneD,
  onReplan,
  onReset,
  onSimulateHazardUpdate,
  isProcessing,
  onStartAutoDemo,
  demoStep,
  onUploadComplete
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
              Simulate disaster intelligence hazard assessment, dataset upload, resource allocation, and dynamic re-planning.
            </p>
          </div>
        </div>

        {/* Action Buttons Group */}
        <div className="flex flex-wrap items-center gap-2.5 w-full lg:w-auto justify-end">
          
          {/* Dataset Upload Component */}
          <DatasetUpload
            onUploadComplete={onUploadComplete}
            metadata={systemState?.dataset_metadata}
          />

          {/* Simulate Hazard Update Button (Rainfall Increase) */}
          <button
            onClick={onSimulateHazardUpdate}
            disabled={isProcessing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/40 text-blue-300 hover:text-white text-xs font-mono font-semibold transition-all cursor-pointer shadow-sm"
            title="Simulate +50mm rainfall surge and elevated flood level"
          >
            <CloudRain className="w-3.5 h-3.5 text-blue-400" />
            <span>🌧️ SURGE RAINFALL (+50mm)</span>
          </button>

          {/* Start Response Simulation Button */}
          <button
            onClick={onStartAutoDemo}
            disabled={isProcessing}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-purple-500/25 transition-all duration-200 cursor-pointer font-mono"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>[ ▶ START RESPONSE SIMULATION ]</span>
          </button>

          {/* Initial Plan Button */}
          {!hasPlan && (
            <button
              onClick={onRunPlan}
              disabled={isProcessing}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs shadow-lg shadow-cyan-600/25 transition-all duration-200 cursor-pointer font-mono"
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
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs shadow-lg shadow-amber-600/25 transition-all duration-200 cursor-pointer font-mono"
            >
              <PlusCircle className="w-4 h-4" />
              <span>[ + ADD NEW DISASTER ZONE ]</span>
            </button>
          ) : (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-mono font-medium">
              <AlertTriangle className="w-4 h-4 text-amber-400 animate-bounce" />
              <span>ZONE D DETECTED</span>
            </div>
          )}

          {/* Re-plan Button */}
          {isPendingReplan && (
            <button
              onClick={onReplan}
              disabled={isProcessing}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold text-xs shadow-xl shadow-red-600/30 transition-all duration-200 transform hover:scale-105 animate-pulse cursor-pointer font-mono"
            >
              <Zap className="w-4 h-4 fill-current" />
              <span>[ 🔄 RE-PLAN RESPONSE ]</span>
            </button>
          )}

        </div>

      </div>
    </div>
  );
}
