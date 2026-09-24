import React from 'react';
import { Truck, Stethoscope, Home, Package, ShieldCheck, AlertCircle } from 'lucide-react';

export default function ResourcePanel({ systemState }) {
  const resources = systemState?.resources || { vehicles: 5, medics: 10, shelters: 3, supplies: 100 };
  const plan = systemState?.current_plan;

  // Calculate allocated resources from current plan
  let allocated = { vehicles: 0, medics: 0, shelters: 0, supplies: 0 };
  if (plan?.final_allocations) {
    allocated.vehicles = plan.final_allocations.reduce((sum, a) => sum + (a.vehicles || 0), 0);
    allocated.medics = plan.final_allocations.reduce((sum, a) => sum + (a.medics || 0), 0);
    allocated.shelters = plan.final_allocations.reduce((sum, a) => sum + (a.shelter_units || 0), 0);
    allocated.supplies = plan.final_allocations.reduce((sum, a) => sum + (a.supplies || 0), 0);
  }

  const items = [
    {
      id: 'vehicles',
      name: 'Rescue Vehicles',
      icon: Truck,
      allocated: allocated.vehicles,
      total: resources.vehicles,
      unit: 'Units',
      color: 'bg-cyan-500',
      textColor: 'text-cyan-400',
      borderColor: 'border-cyan-500/30'
    },
    {
      id: 'medics',
      name: 'Medics / Triage Teams',
      icon: Stethoscope,
      allocated: allocated.medics,
      total: resources.medics,
      unit: 'Personnel',
      color: 'bg-rose-500',
      textColor: 'text-rose-400',
      borderColor: 'border-rose-500/30'
    },
    {
      id: 'shelters',
      name: 'Emergency Shelters',
      icon: Home,
      allocated: allocated.shelters,
      total: resources.shelters,
      unit: 'Facilities',
      color: 'bg-emerald-500',
      textColor: 'text-emerald-400',
      borderColor: 'border-emerald-500/30'
    },
    {
      id: 'supplies',
      name: 'Supply Units',
      icon: Package,
      allocated: allocated.supplies,
      total: resources.supplies,
      unit: 'Packages',
      color: 'bg-amber-500',
      textColor: 'text-amber-400',
      borderColor: 'border-amber-500/30'
    }
  ];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl glass-card">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
            Resource Inventory Monitor
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
          Hard Constraints Enforced
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {items.map((item) => {
          const Icon = item.icon;
          const percentage = Math.min(100, Math.round((item.allocated / (item.total || 1)) * 100));
          const isAtLimit = item.allocated >= item.total && item.total > 0;

          return (
            <div
              key={item.id}
              className={`rounded-xl p-4 bg-slate-800/60 border ${item.borderColor} relative overflow-hidden transition-all`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={`p-2 rounded-lg bg-slate-900 ${item.textColor}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-xs font-bold text-slate-200">{item.name}</span>
                </div>
                {isAtLimit && (
                  <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
                    MAX CAP
                  </span>
                )}
              </div>

              {/* Allocation values */}
              <div className="flex items-baseline justify-between mt-3 mb-2 font-mono">
                <span className="text-2xl font-black text-white">
                  {item.allocated} <span className="text-xs font-normal text-slate-400">/ {item.total}</span>
                </span>
                <span className={`text-xs font-bold ${isAtLimit ? 'text-amber-400' : 'text-slate-400'}`}>
                  {percentage}%
                </span>
              </div>

              {/* Progress Bar */}
              <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isAtLimit ? 'bg-amber-500' : item.color
                  }`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
