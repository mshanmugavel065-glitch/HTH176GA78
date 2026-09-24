import React, { useState } from 'react';
import { HelpCircle, Brain, AlertTriangle, Scale, CheckCircle2, ChevronDown, ChevronUp, Layers } from 'lucide-react';

export default function DecisionExplanation({ plan, systemState }) {
  const [isOpen, setIsOpen] = useState(true);

  if (!plan) return null;

  const conflicts = plan.conflicts || [];
  const tradeoffs = plan.agent_tradeoffs || {};
  const explanation = plan.explanation || '';
  const changes = plan.changes || [];
  const recs = systemState?.agent_recommendations || {};

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl glass-card space-y-4">
      
      {/* Header Bar with Toggle */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between cursor-pointer border-b border-slate-800 pb-3 group"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center shadow-md">
            <HelpCircle className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              Why did the AI make this decision?
              <span className="text-[10px] font-normal px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                Explainable AI (XAI)
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Transparent multi-agent decision trace, conflict resolutions, and trade-off rationales.
            </p>
          </div>
        </div>
        <button className="p-1 rounded-lg bg-slate-800 text-slate-400 group-hover:text-white transition-colors">
          {isOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>
      </div>

      {/* Expandable Explanation Body */}
      {isOpen && (
        <div className="space-y-4 pt-1 font-mono">
          
          {/* Master Reasoning Box */}
          <div className="bg-slate-950/80 border border-purple-500/30 rounded-xl p-4 shadow-inner">
            <div className="flex items-center gap-2 text-xs font-bold text-purple-300 mb-2">
              <Brain className="w-4 h-4 text-purple-400" />
              COORDINATOR DECISION RATIONALE
            </div>
            <p className="text-xs text-slate-200 leading-relaxed font-sans">
              {explanation}
            </p>
          </div>

          {/* Conflict & Resolution Grid */}
          {conflicts.length > 0 && (
            <div className="space-y-2">
              <span className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Resource Conflicts Resolved ({conflicts.length})
              </span>
              <div className="grid grid-cols-1 gap-2">
                {conflicts.map((conf) => (
                  <div key={conf.id} className="bg-amber-950/20 border border-amber-500/30 rounded-xl p-3 text-xs">
                    <div className="flex items-center justify-between text-amber-300 font-bold mb-1">
                      <span>Conflict: {conf.resource_type.toUpperCase()} OVER-ALLOCATION</span>
                      <span className="text-[10px] bg-amber-500/20 px-2 py-0.5 rounded border border-amber-500/40">
                        Demanded: {conf.demanded} / Available: {conf.available}
                      </span>
                    </div>
                    <p className="text-slate-300 text-[11px] mb-2">{conf.description}</p>
                    <div className="bg-slate-900/90 p-2 rounded border border-slate-800 text-emerald-300 text-[11px] flex items-start gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span><strong>Coordinator Resolution:</strong> {conf.resolution}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Trade-offs Made */}
          {tradeoffs && Object.keys(tradeoffs).length > 0 && (
            <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 text-xs">
              <span className="font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5 mb-2">
                <Scale className="w-4 h-4 text-cyan-400" /> Key Multi-Agent Trade-offs
              </span>
              <ul className="space-y-1.5 text-[11px] text-slate-300 list-disc list-inside font-sans">
                {Object.entries(tradeoffs).map(([key, val]) => (
                  <li key={key} className="leading-relaxed">
                    <strong className="text-slate-200 capitalize">{key.replace(/_/g, ' ')}:</strong> {val}
                  </li>
                ))}
              </ul>
            </div>
          )}

        </div>
      )}

    </div>
  );
}
