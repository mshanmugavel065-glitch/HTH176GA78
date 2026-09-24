import React from 'react';
import { ShieldAlert, RefreshCw, Radio, MapPin, Database } from 'lucide-react';

export default function Header({ systemState, onReset, isProcessing }) {
  const location = systemState?.location ? systemState.location : 'Location not set';
  const isAnalyzed = Boolean(systemState?.is_analyzed && systemState?.location);
  const activeAgents = systemState?.active_agents_count || 4;

  return (
    <header className="bg-slate-900/95 border-b border-slate-800 backdrop-blur-md sticky top-0 z-40 px-4 sm:px-6 py-3 shadow-xl font-sans">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        
        {/* Title and Branding */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-blue-600 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <ShieldAlert className="w-6 h-6 text-white" />
            </div>
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white tracking-wider font-mono">RESQ-AI</h1>
              <span className="px-2 py-0.5 text-[10px] uppercase font-mono font-semibold tracking-wider rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                Multi-Agent Coordinator
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Multi-Agent Disaster Response Coordinator
            </p>
          </div>
        </div>

        {/* Current Location & System Status Badges */}
        <div className="flex flex-wrap items-center gap-2.5">
          
          {/* Active Location Badge */}
          <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-mono transition-all ${
            isAnalyzed
              ? 'bg-slate-800/90 border-cyan-500/40 text-cyan-300'
              : 'bg-slate-800/50 border-slate-700 text-slate-400'
          }`}>
            <MapPin className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-400">Location:</span>
            <span className="font-bold text-white">{location}</span>
          </div>

          {/* Coordination Active */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/90 border border-slate-700/80 text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span className="text-slate-400 font-mono">Status:</span>
            <span className="text-emerald-400 font-semibold font-mono">● Coordination Active</span>
          </div>

          {/* Agents Badge */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/90 border border-slate-700/80 text-xs">
            <Radio className="w-3.5 h-3.5 text-purple-400" />
            <span className="text-slate-400 font-mono">Agents:</span>
            <span className="text-purple-300 font-bold font-mono">{activeAgents} Active</span>
          </div>

          {/* Reset Button */}
          <button
            onClick={onReset}
            disabled={isProcessing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-slate-300 hover:text-white transition-all disabled:opacity-50 cursor-pointer"
            title="Reset active scenario"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isProcessing ? 'animate-spin' : ''}`} />
            Reset
          </button>

        </div>

      </div>

      {/* Data Source Indicator Banner */}
      <div className="max-w-7xl mx-auto mt-2 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400 font-mono">
        <div className="flex items-center gap-2">
          <Database className="w-3.5 h-3.5 text-cyan-400" />
          <span>Live Data: <span className="text-amber-400">Unavailable</span> • <strong className="text-cyan-300 uppercase">SIMULATED DISASTER SCENARIO</strong></span>
        </div>
        <span className="hidden sm:inline text-slate-500">
          Deterministic Hard Constraints Enforced
        </span>
      </div>
    </header>
  );
}
