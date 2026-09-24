import React from 'react';
import { CloudRain, Waves, Maximize2, AlertTriangle, ShieldAlert, Activity, CheckCircle, Info } from 'lucide-react';

export default function DisasterIntelligencePanel({ systemState }) {
  const intel = systemState?.intelligence_result;
  const zones = systemState?.zones || [];
  const location = systemState?.location || 'Unknown Location';
  const disasterType = systemState?.disaster_type || 'Flood';

  if (!intel && zones.length === 0) return null;

  const score = intel?.overall_severity_score || 0.0;
  const riskLevel = intel?.overall_risk_level || 'Moderate';
  const maxRainfall = intel?.max_rainfall_mm || (zones.length ? Math.max(...zones.map(z => z.rainfall_mm || 0)) : 0);
  const maxFlood = intel?.max_flood_level_m || (zones.length ? Math.max(...zones.map(z => z.flood_level_m || 0)) : 0);
  const totalArea = intel?.total_affected_area_km2 || (zones.length ? zones.reduce((acc, z) => acc + (z.affected_area_km2 || 0), 0) : 0);

  const getRiskBadgeColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'critical': return 'bg-rose-500/20 text-rose-300 border-rose-500/50';
      case 'very high': return 'bg-orange-500/20 text-orange-300 border-orange-500/50';
      case 'high': return 'bg-amber-500/20 text-amber-300 border-amber-500/50';
      case 'moderate': return 'bg-blue-500/20 text-blue-300 border-blue-500/50';
      default: return 'bg-slate-500/20 text-slate-300 border-slate-500/50';
    }
  };

  const factors = intel?.contributing_factors || {
    'Rainfall': 'Very High',
    'Flood Level': 'High',
    'Affected Area': 'High',
    'Medical Urgency': 'Moderate',
    'Road Accessibility': 'Restricted'
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6 relative overflow-hidden">
      
      {/* Background Accent */}
      <div className="absolute -top-24 -right-24 w-72 h-72 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
            <h2 className="text-lg font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <CloudRain className="w-5 h-5 text-cyan-400" />
              DISASTER INTELLIGENCE & HAZARD ASSESSMENT
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Analyzing environmental measurement telemetry & multi-factor hazard indicators for <strong className="text-white">{location}</strong>
          </p>
        </div>

        {/* Risk Badge */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <span className="text-[11px] text-slate-400 uppercase font-mono block">Simulated Severity</span>
            <span className="text-2xl font-black font-mono text-white">{score} <span className="text-xs text-slate-400 font-normal">/ 100</span></span>
          </div>
          <span className={`px-3 py-1.5 rounded-lg border font-mono font-bold text-xs uppercase tracking-wider ${getRiskBadgeColor(riskLevel)}`}>
            {riskLevel}
          </span>
        </div>
      </div>

      {/* Top 4 Telemetry Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        
        {/* Rainfall Card */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 space-y-1.5 relative">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>Peak Rainfall</span>
            <CloudRain className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-cyan-300">
            {maxRainfall} <span className="text-xs text-slate-400 font-normal">mm</span>
          </div>
          <p className="text-[11px] text-slate-500 font-mono">Measured precipitation</p>
        </div>

        {/* Flood Level Card */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 space-y-1.5 relative">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>Peak Flood Level</span>
            <Waves className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-blue-300">
            {maxFlood} <span className="text-xs text-slate-400 font-normal">m</span>
          </div>
          <p className="text-[11px] text-slate-500 font-mono">Standing water accumulation</p>
        </div>

        {/* Affected Area Card */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 space-y-1.5 relative">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>Affected Area</span>
            <Maximize2 className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-purple-300">
            {totalArea} <span className="text-xs text-slate-400 font-normal">km²</span>
          </div>
          <p className="text-[11px] text-slate-500 font-mono">Total inundated footprint</p>
        </div>

        {/* Priority Zone Card */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 space-y-1.5 relative">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>Priority Sector</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-xl font-bold font-mono text-rose-400 truncate">
            {intel?.priority_zone_name || 'Zone B'}
          </div>
          <p className="text-[11px] text-slate-500 font-mono">Immediate emergency focus</p>
        </div>

      </div>

      {/* Risk Factor Breakdown & Assessment Rationale */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-2">
        
        {/* Contributing Risk Factors List */}
        <div className="lg:col-span-1 bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-3">
          <h3 className="text-xs font-bold text-slate-300 uppercase font-mono tracking-wider flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-cyan-400" />
            Contributing Risk Factors
          </h3>
          <div className="space-y-2 font-mono text-xs">
            {Object.entries(factors).map(([factor, level]) => (
              <div key={factor} className="flex items-center justify-between border-b border-slate-800/60 pb-1.5">
                <span className="text-slate-400">{factor}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  level.includes('High') || level.includes('Critical') || level.includes('Impaired')
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                }`}>
                  {level}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Explanation Rationale Box */}
        <div className="lg:col-span-2 bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-3 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold text-slate-300 uppercase font-mono tracking-wider flex items-center gap-1.5 mb-2">
              <Info className="w-4 h-4 text-cyan-400" />
              Intelligence Rationale & Sector Prioritization
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed font-sans bg-slate-900/60 p-3 rounded-lg border border-slate-800/80">
              {intel?.explanation || `Elevated precipitation and flood level combined with critical casualty density designate ${intel?.priority_zone_name || 'Zone B'} as the immediate priority sector.`}
            </p>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono pt-2 border-t border-slate-800/60">
            <span>Model: <strong className="text-slate-400">Prototype Risk Score Model</strong></span>
            <span>Multi-Factor Weighted Assessment</span>
          </div>
        </div>

      </div>

      {/* Visual Bar Charts: Rainfall & Flood Levels across Zones */}
      <div className="pt-4 border-t border-slate-800 space-y-3">
        <h3 className="text-xs font-bold text-slate-300 uppercase font-mono tracking-wider">
          Hazard Distribution Across Active Sectors
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          
          {/* Rainfall Distribution Chart */}
          <div className="bg-slate-950/40 p-4 rounded-xl border border-slate-800/60 space-y-2">
            <span className="text-xs font-mono text-cyan-400 font-semibold block">Rainfall (mm) by Sector</span>
            <div className="space-y-2 pt-1">
              {zones.map((z) => {
                const maxVal = Math.max(...zones.map(z => z.rainfall_mm || 1), 300);
                const pct = Math.min(100, Math.round(((z.rainfall_mm || 0) / maxVal) * 100));
                return (
                  <div key={z.id} className="space-y-1">
                    <div className="flex justify-between text-[11px] font-mono text-slate-300">
                      <span>{z.name}</span>
                      <span>{z.rainfall_mm} mm</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-cyan-500 h-full rounded-full transition-all duration-500"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Flood Level Distribution Chart */}
          <div className="bg-slate-950/40 p-4 rounded-xl border border-slate-800/60 space-y-2">
            <span className="text-xs font-mono text-blue-400 font-semibold block">Flood Level (m) by Sector</span>
            <div className="space-y-2 pt-1">
              {zones.map((z) => {
                const maxVal = Math.max(...zones.map(z => z.flood_level_m || 1), 5);
                const pct = Math.min(100, Math.round(((z.flood_level_m || 0) / maxVal) * 100));
                return (
                  <div key={z.id} className="space-y-1">
                    <div className="flex justify-between text-[11px] font-mono text-slate-300">
                      <span>{z.name}</span>
                      <span>{z.flood_level_m} m</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-blue-500 h-full rounded-full transition-all duration-500"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

        </div>
      </div>

    </div>
  );
}
