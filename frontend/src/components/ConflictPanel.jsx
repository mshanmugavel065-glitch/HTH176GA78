import React from 'react';
import { AlertOctagon, Scale, CheckCircle2, ShieldAlert, Users, Truck, HeartPulse, Megaphone } from 'lucide-react';

export default function ConflictPanel({ plan }) {
  if (!plan) return null;

  const conflicts = plan.conflicts || [];
  const negotiation = plan.agent_negotiation;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl glass-card space-y-4">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Scale className="w-5 h-5 text-amber-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
            Multi-Agent Conflict Resolution & Trade-off Matrix
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
              {conflicts.length} Conflicts Handled
            </span>
          </h3>
        </div>
        <span className="text-xs font-mono text-slate-400">Fixed Limit Solver</span>
      </div>

      {/* Multi-Agent Negotiation Summary */}
      {negotiation && (
        <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 font-mono space-y-3">
          <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider block">
            Agent Demands & Negotiation Trace:
          </span>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            {/* Medical Agent Demand */}
            <div className="bg-rose-950/20 border border-rose-500/30 p-3 rounded-lg">
              <div className="flex items-center gap-1.5 text-rose-400 font-bold mb-1">
                <HeartPulse className="w-4 h-4" /> Medical Agent Demand
              </div>
              <p className="text-slate-300 text-[11px] leading-relaxed">{negotiation.medical_request}</p>
            </div>

            {/* Logistics Agent Demand */}
            <div className="bg-cyan-950/20 border border-cyan-500/30 p-3 rounded-lg">
              <div className="flex items-center gap-1.5 text-cyan-400 font-bold mb-1">
                <Truck className="w-4 h-4" /> Logistics Agent Demand
              </div>
              <p className="text-slate-300 text-[11px] leading-relaxed">{negotiation.logistics_request}</p>
            </div>

            {/* Communications Agent Demand */}
            <div className="bg-amber-950/20 border border-amber-500/30 p-3 rounded-lg">
              <div className="flex items-center gap-1.5 text-amber-400 font-bold mb-1">
                <Megaphone className="w-4 h-4" /> Communications Agent Demand
              </div>
              <p className="text-slate-300 text-[11px] leading-relaxed">{negotiation.comm_request}</p>
            </div>
          </div>

          {/* Coordinator Synthesis Resolution */}
          <div className="bg-purple-950/30 border border-purple-500/40 p-3 rounded-lg text-xs text-purple-200 flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-purple-300 font-bold">Coordinator Resolution:</strong>{' '}
              {negotiation.coordinator_resolution}
            </div>
          </div>
        </div>
      )}

      {/* Explicit Resource Conflicts List */}
      {conflicts.length > 0 && (
        <div className="space-y-2 font-mono">
          {conflicts.map((conf) => (
            <div key={conf.id} className="bg-amber-950/20 border border-amber-500/40 rounded-xl p-3 text-xs">
              <div className="flex items-center justify-between text-amber-300 font-bold mb-1">
                <span>⚠️ RESOURCE CONFLICT: {conf.resource_type.toUpperCase()}</span>
                <span className="text-[10px] bg-amber-500/20 px-2 py-0.5 rounded border border-amber-500/40 font-bold">
                  Requested: {conf.demanded} / Max Available: {conf.available}
                </span>
              </div>
              <p className="text-slate-300 text-[11px] mb-2">{conf.description}</p>
              <div className="bg-slate-900/90 p-2 rounded border border-slate-800 text-emerald-300 text-[11px] flex items-start gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span><strong>Coordinator Trade-off Solution:</strong> {conf.resolution}</span>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
