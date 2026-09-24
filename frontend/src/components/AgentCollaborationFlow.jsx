import React from 'react';
import { HeartPulse, Truck, Megaphone, Brain, ArrowDown, ArrowRight, ArrowUp, CheckCircle, Clock } from 'lucide-react';

export default function AgentCollaborationFlow({ systemState, isProcessing, activeAgent }) {
  const recommendations = systemState?.agent_recommendations || {};
  const currentPlan = systemState?.current_plan;

  const agents = [
    {
      id: 'medical_agent',
      name: 'Medical Agent',
      icon: HeartPulse,
      role: 'Triage & Medic Allocation',
      color: 'from-rose-500 to-red-600',
      borderColor: 'border-rose-500/40',
      bgGlow: 'shadow-rose-500/20',
      badge: 'Triage Focus',
      status: recommendations['medical_agent'] ? 'Completed' : (activeAgent === 'medical' ? 'Analyzing...' : 'Ready')
    },
    {
      id: 'logistics_agent',
      name: 'Logistics Agent',
      icon: Truck,
      role: 'Vehicles, Shelters & Supplies',
      color: 'from-blue-500 to-cyan-600',
      borderColor: 'border-cyan-500/40',
      bgGlow: 'shadow-cyan-500/20',
      badge: 'Resource Logistics',
      status: recommendations['logistics_agent'] ? 'Completed' : (activeAgent === 'logistics' ? 'Analyzing...' : 'Ready')
    },
    {
      id: 'communication_agent',
      name: 'Communication Agent',
      icon: Megaphone,
      role: 'Evacuation Alerts & Public Safety',
      color: 'from-amber-500 to-orange-600',
      borderColor: 'border-amber-500/40',
      bgGlow: 'shadow-amber-500/20',
      badge: 'Public Messaging',
      status: recommendations['communication_agent'] ? 'Completed' : (activeAgent === 'communication' ? 'Analyzing...' : 'Ready')
    },
  ];

  const isCoordinatorActive = activeAgent === 'coordinator';
  const isCoordinatorDone = Boolean(currentPlan);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl glass-card relative overflow-hidden">
      
      {/* Header Title */}
      <div className="flex items-center justify-between mb-5 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
            Multi-Agent Collaboration Network
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-xs text-slate-400 font-mono">Parallel Agent Reasoning Engine</span>
        </div>
      </div>

      {/* Visual Multi-Agent Flow Diagram */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center relative">
        
        {/* Specialized Agents (Columns 1 to 3) */}
        <div className="md:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-3">
          {agents.map((agent) => {
            const Icon = agent.icon;
            const isAnalyzing = activeAgent === agent.id.replace('_agent', '');
            const hasOutput = Boolean(recommendations[agent.id]);

            return (
              <div
                key={agent.id}
                className={`relative rounded-xl p-4 border transition-all duration-300 ${
                  isAnalyzing
                    ? `${agent.borderColor} bg-slate-800/90 shadow-xl ${agent.bgGlow} scale-105 ring-2 ring-cyan-400/50`
                    : hasOutput
                    ? 'border-slate-700 bg-slate-800/60'
                    : 'border-slate-800 bg-slate-900/50 opacity-80'
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${agent.color} flex items-center justify-center shadow-md`}>
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold ${
                    isAnalyzing
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 animate-pulse'
                      : hasOutput
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : 'bg-slate-800 text-slate-400 border border-slate-700'
                  }`}>
                    {isAnalyzing ? 'Thinking...' : hasOutput ? 'Finished' : 'Standby'}
                  </span>
                </div>

                <h4 className="text-xs font-bold text-white font-mono">{agent.name}</h4>
                <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{agent.role}</p>

                {/* Agent recommendation count badge */}
                {recommendations[agent.id] && (
                  <div className="mt-3 pt-2 border-t border-slate-700/60 text-[10px] text-slate-300 flex items-center justify-between font-mono">
                    <span>Recommendations:</span>
                    <span className="text-cyan-400 font-bold">
                      {recommendations[agent.id].recommendations?.length || 0} Zones
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Connector Arrow to Coordinator */}
        <div className="hidden md:flex flex-col items-center justify-center text-cyan-400 pointer-events-none">
          <div className="flex items-center gap-1">
            <span className="text-[10px] font-mono text-cyan-400/80 uppercase font-semibold">Synthesize</span>
            <ArrowRight className={`w-6 h-6 text-cyan-400 ${isProcessing ? 'animate-pulse' : ''}`} />
          </div>
        </div>

        {/* Master Coordinator Agent (Column 4) */}
        <div className={`rounded-xl p-4 border transition-all duration-300 ${
          isCoordinatorActive
            ? 'border-purple-500 bg-purple-950/40 shadow-2xl shadow-purple-500/30 ring-2 ring-purple-400/60 scale-105'
            : isCoordinatorDone
            ? 'border-emerald-500/50 bg-slate-800/90 shadow-xl shadow-emerald-500/10'
            : 'border-slate-800 bg-slate-900/50'
        }`}>
          <div className="flex items-start justify-between mb-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold ${
              isCoordinatorActive
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 animate-pulse'
                : isCoordinatorDone
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                : 'bg-slate-800 text-slate-400'
            }`}>
              {isCoordinatorActive ? 'Resolving...' : isCoordinatorDone ? 'Plan Ready' : 'Standby'}
            </span>
          </div>

          <h4 className="text-xs font-bold text-white font-mono">Coordinator Agent</h4>
          <p className="text-[11px] text-slate-400 mt-1">
            Resolves conflicts & enforces hard resource limits.
          </p>

          {currentPlan && (
            <div className="mt-3 pt-2 border-t border-slate-700/60 text-[10px] text-slate-300 flex items-center justify-between font-mono">
              <span>Conflicts Resolved:</span>
              <span className="text-amber-400 font-bold">
                {currentPlan.conflicts?.length || 0} Items
              </span>
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
