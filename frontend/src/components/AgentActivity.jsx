import React from 'react';
import { Terminal, Bot, HeartPulse, Truck, Megaphone, Brain, AlertOctagon, CheckCircle2, Info } from 'lucide-react';

export default function AgentActivity({ logs }) {
  const getAgentBadge = (agent) => {
    switch (agent) {
      case 'medical':
      case 'medical_agent':
        return { name: 'Medical Agent', icon: HeartPulse, color: 'text-rose-400 border-rose-500/30 bg-rose-500/10', emoji: '🤖' };
      case 'logistics':
      case 'logistics_agent':
        return { name: 'Logistics Agent', icon: Truck, color: 'text-cyan-400 border-cyan-500/30 bg-cyan-500/10', emoji: '🚑' };
      case 'communication':
      case 'communication_agent':
        return { name: 'Communication Agent', icon: Megaphone, color: 'text-amber-400 border-amber-500/30 bg-amber-500/10', emoji: '📢' };
      case 'coordinator':
      case 'coordinator_agent':
        return { name: 'Coordinator Agent', icon: Brain, color: 'text-purple-400 border-purple-500/30 bg-purple-500/10', emoji: '🧠' };
      default:
        return { name: 'System', icon: Bot, color: 'text-slate-400 border-slate-700 bg-slate-800', emoji: '⚙️' };
    }
  };

  const getTypeStyle = (type) => {
    switch (type) {
      case 'conflict':
        return 'border-l-4 border-amber-500 bg-amber-950/20';
      case 'success':
        return 'border-l-4 border-emerald-500 bg-emerald-950/10';
      case 'warning':
        return 'border-l-4 border-rose-500 bg-rose-950/20';
      default:
        return 'border-l-4 border-cyan-500 bg-slate-900/60';
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl glass-card flex flex-col h-[400px]">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3 shrink-0">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-purple-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
            Agent Reasoning & Activity Feed
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
          Live Stream
        </span>
      </div>

      {/* Log Feed Stream */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 font-mono text-xs">
        {logs && logs.length > 0 ? (
          logs.map((log) => {
            const badge = getAgentBadge(log.agent);
            const Icon = badge.icon;
            const typeStyle = getTypeStyle(log.type);

            return (
              <div
                key={log.id || Math.random()}
                className={`p-3 rounded-xl border border-slate-800/80 ${typeStyle} transition-all hover:bg-slate-800/40`}
              >
                <div className="flex items-center justify-between gap-2 mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-base">{badge.emoji}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badge.color}`}>
                      {badge.name}
                    </span>
                    <span className="text-white font-bold text-xs">{log.action}</span>
                  </div>
                  <span className="text-[10px] text-slate-400 shrink-0">{log.timestamp}</span>
                </div>
                <p className="text-slate-300 text-[11px] pl-6 leading-relaxed">
                  {log.details}
                </p>
              </div>
            );
          })
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 italic">
            <Bot className="w-8 h-8 text-slate-600 mb-2 animate-bounce" />
            <span>No agent activity logged yet. Click "RUN INITIAL AGENTS" or "START DEMO".</span>
          </div>
        )}
      </div>

    </div>
  );
}
