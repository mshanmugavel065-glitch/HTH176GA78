import React from 'react';
import { CloudRain, HeartPulse, Truck, Megaphone, Brain, ArrowRight, ShieldCheck } from 'lucide-react';

export default function AgentNetwork({ systemState, isProcessing, activeAgent }) {
  const recommendations = systemState?.agent_recommendations || {};
  const currentPlan = systemState?.current_plan;

  const agents = [
    {
      id: 'disaster_intelligence_agent',
      name: 'Disaster Intelligence Agent',
      icon: CloudRain,
      role: 'Hazard Telemetry & Severity Score Model',
      color: 'from-cyan-500 to-blue-600',
      badge: 'Disaster Intelligence'
    },
    {
      id: 'medical_agent',
      name: 'Medical Agent',
      icon: HeartPulse,
      role: 'Trauma Triage & Field Medic Allocation',
      color: 'from-rose-500 to-red-600',
      badge: 'Medical Triage'
    },
    {
      id: 'logistics_agent',
      name: 'Logistics Agent',
      icon: Truck,
      role: 'Rescue Fleet, Shelters & Evacuation Routes',
      color: 'from-amber-500 to-orange-600',
      badge: 'Fleet Logistics'
    },
    {
      id: 'communication_agent',
      name: 'Communication Agent',
      icon: Megaphone,
      role: 'Public Safety Alerts & Evacuation Advisories',
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
            5-Agent Multi-Agent Collaboration Network
            <span className="text-[10px] font-normal px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
              5 Specialized AI Agents
            </span>
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-xs text-slate-400 font-mono">Parallel Reasoning Pipeline</span>
        </div>
      </div>

      {/* Grid of 4 Specialized Agents + Master Coordinator */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 items-center">
        
        {/* Left Side: 4 Specialized Agents */}
        <div className="lg:col-span-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
          {agents.map((agent) => {
            const Icon = agent.icon;
            const hasRec = Boolean(recommendations[agent.id]);

            return (
              <div
                key={agent.id}
                className={`rounded-xl p-3.5 border transition-all duration-300 ${
                  hasRec
                    ? 'border-cyan-500/40 bg-slate-800/80 shadow-md'
                    : 'border-slate-800/80 bg-slate-900/50'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className={`p-2 rounded-lg bg-gradient-to-tr ${agent.color} text-white shadow-md`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    {agent.badge}
                  </span>
                </div>
                <h4 className="text-xs font-bold text-white font-mono">{agent.name}</h4>
                <p className="text-[11px] text-slate-400 mt-1">{agent.role}</p>

                {hasRec && (
                  <div className="mt-2.5 pt-2 border-t border-slate-800 text-[10px] font-mono text-emerald-400 flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3" /> Analysis Complete
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Right Side: Master Coordinator Agent */}
        <div className="lg:col-span-1 bg-gradient-to-b from-purple-950/40 via-slate-900 to-slate-900 border border-purple-500/40 rounded-xl p-4 text-center relative overflow-hidden flex flex-col items-center justify-center space-y-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 text-white flex items-center justify-center shadow-lg shadow-purple-500/30">
            <Brain className="w-6 h-6" />
          </div>

          <div>
            <h4 className="text-xs font-bold text-white font-mono uppercase tracking-wider">
              Coordinator Agent
            </h4>
            <p className="text-[11px] text-slate-400 mt-1">
              Master Orchestration, Conflict Resolution & Hard Resource Validator
            </p>
          </div>

          <div className="w-full pt-2 border-t border-purple-500/20 text-[10px] font-mono text-cyan-300">
            {currentPlan ? 'Plan Validated under Hard Bounds' : 'Awaiting Agent Synthesis'}
          </div>
        </div>

      </div>

    </div>
  );
}
