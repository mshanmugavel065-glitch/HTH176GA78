import React from 'react';
import { MapPin, AlertOctagon, HeartPulse, Truck, ShieldAlert, Megaphone, Brain, ArrowRight } from 'lucide-react';

export default function AgentNetwork({ systemState, isProcessing, activeAgent }) {
  const recommendations = systemState?.agent_recommendations || {};
  const currentPlan = systemState?.current_plan;

  const agents = [
    {
      id: 'location_agent',
      name: 'Location Intelligence Agent',
      icon: MapPin,
      role: 'Geographic Sectoring & Corridor Mapping',
      color: 'from-blue-500 to-indigo-600',
      badge: 'GIS Analysis'
    },
    {
      id: 'situation_agent',
      name: 'Situation / Incident Agent',
      icon: AlertOctagon,
      role: 'Incident Categorization & Severity Triage',
      color: 'from-cyan-500 to-teal-600',
      badge: 'Incident Report'
    },
    {
      id: 'medical_agent',
      name: 'Medical Agent',
      icon: HeartPulse,
      role: 'Casualty Density & Medic Allocation',
      color: 'from-rose-500 to-red-600',
      badge: 'Medical Triage'
    },
    {
      id: 'logistics_agent',
      name: 'Logistics Agent',
      icon: Truck,
      role: 'Vehicles, Shelters & Supply Chain',
      color: 'from-amber-500 to-orange-600',
      badge: 'Fleet Logistics'
    },
    {
      id: 'risk_agent',
      name: 'Risk Agent',
      icon: ShieldAlert,
      role: 'Compound Hazard Matrix & Priority Ranking',
      color: 'from-emerald-500 to-green-600',
      badge: 'Risk Matrix'
    },
    {
      id: 'communication_agent',
      name: 'Communication Agent',
      icon: Megaphone,
      role: 'Public Safety Warnings & Advisories',
      color: 'from-violet-500 to-purple-600',
      badge: 'Alert Broadcast'
    }
  ];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl glass-card relative overflow-hidden">
      
      {/* Header Title */}
      <div className="flex items-center justify-between mb-5 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
            7-Agent Multi-Agent Collaboration Network
            <span className="text-[10px] font-normal px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
              7 Active Agents
            </span>
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-xs text-slate-400 font-mono">Parallel Reasoning Pipeline</span>
        </div>
      </div>

      {/* Grid of 6 Specialized Agents + Coordinator */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 items-center">
        
        {/* Left Side: 6 Specialized Agents (2 rows of 3) */}
        <div className="lg:col-span-3 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {agents.map((agent) => {
            const Icon = agent.icon;
            const hasRec = Boolean(recommendations[agent.id]);
            const isAnalyzing = activeAgent === agent.id.replace('_agent', '');

            return (
              <div
                key={agent.id}
                className={`rounded-xl p-3.5 border transition-all duration-300 ${
                  isAnalyzing
                    ? 'border-purple-500 bg-purple-950/40 shadow-lg scale-105 ring-2 ring-purple-500/50'
                    : hasRec
                    ? 'border-slate-700 bg-slate-800/60'
                    : 'border-slate-800/80 bg-slate-900/50'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${agent.color} flex items-center justify-center shadow-md`}>
                    <Icon className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                    {agent.badge}
                  </span>
                </div>
                <h4 className="text-xs font-bold text-white font-mono">{agent.name}</h4>
                <p className="text-[10px] text-slate-400 mt-0.5 line-clamp-2">{agent.role}</p>
              </div>
            );
          })}
        </div>

        {/* Right Side: Central Coordinator Orchestrator */}
        <div className="lg:col-span-1 rounded-xl p-4 border border-purple-500/40 bg-purple-950/20 glass-card-glow-cyan">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-white font-mono">Coordinator Agent</h4>
              <span className="text-[10px] text-purple-300 font-mono">Master Orchestrator</span>
            </div>
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed font-sans">
            Aggregates all 6 agent inputs, resolves conflicts, and enforces hard limits.
          </p>
          {currentPlan && (
            <div className="mt-3 pt-2 border-t border-purple-500/30 text-[10px] text-purple-300 font-mono flex items-center justify-between">
              <span>Conflicts Resolved:</span>
              <span className="font-bold text-amber-400">{currentPlan.conflicts?.length || 0}</span>
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
