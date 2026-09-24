import React, { useState } from 'react';
import { ShieldAlert, MapPin, FileText, Sparkles, ArrowRight, AlertCircle } from 'lucide-react';

export default function HeroLanding({ onAnalyze, isProcessing }) {
  const [location, setLocation] = useState('');
  const [situation, setSituation] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setErrorMsg('');

    if (!location.trim()) {
      setErrorMsg('Please enter a disaster-response location.');
      return;
    }
    if (!situation.trim()) {
      setErrorMsg('Please describe the disaster situation.');
      return;
    }

    onAnalyze(location.trim(), situation.trim());
  };

  const handleQuickExample = (loc, sit) => {
    setLocation(loc);
    setSituation(sit);
    setErrorMsg('');
  };

  return (
    <div className="max-w-4xl mx-auto my-6 p-6 sm:p-8 rounded-3xl bg-slate-900/95 border border-slate-800 shadow-2xl glass-card relative overflow-hidden font-sans">
      
      {/* Glow Effects */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header Banner */}
      <div className="text-center space-y-3 mb-8 relative z-10">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-bold tracking-wider uppercase shadow-md">
          <ShieldAlert className="w-4 h-4 text-cyan-400 animate-pulse" />
          RESQ-AI Command Center
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white font-mono tracking-tight">
          Multi-Agent Disaster Response Coordinator
        </h1>
        <p className="text-sm text-slate-400 max-w-xl mx-auto leading-relaxed">
          "Describe a location or situation and I'll help you understand it and create a response plan."
        </p>
      </div>

      {/* Validation Error Banner */}
      {errorMsg && (
        <div className="mb-6 p-3.5 rounded-xl bg-red-950/40 border border-red-500/50 text-red-300 text-xs font-mono flex items-center gap-2 animate-pulse relative z-10">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Form Input Section */}
      <form onSubmit={handleSubmit} className="space-y-6 relative z-10">
        
        {/* Location Input */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono flex items-center gap-2">
            <MapPin className="w-4 h-4 text-cyan-400" /> LOCATION
          </label>
          <div className="relative">
            <input
              type="text"
              value={location}
              onChange={(e) => {
                setLocation(e.target.value);
                if (errorMsg) setErrorMsg('');
              }}
              placeholder="Enter city, state / country... (e.g. Chennai, Tamil Nadu)"
              className="w-full bg-slate-950/80 border border-slate-700 focus:border-cyan-500 rounded-xl px-4 py-3.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 font-sans transition-all"
            />
          </div>
          <p className="text-[11px] text-slate-500 font-mono">
            Examples: Chennai, Tamil Nadu • Mumbai, Maharashtra • Bengaluru, Karnataka • Kochi, Kerala • Hyderabad, Telangana
          </p>
        </div>

        {/* Situation Input */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono flex items-center gap-2">
            <FileText className="w-4 h-4 text-purple-400" /> DISASTER SITUATION
          </label>
          <textarea
            rows={3}
            value={situation}
            onChange={(e) => {
              setSituation(e.target.value);
              if (errorMsg) setErrorMsg('');
            }}
            placeholder="Describe the disaster situation... (e.g. Heavy flooding affecting multiple regions with limited rescue resources)"
            className="w-full bg-slate-950/80 border border-slate-700 focus:border-purple-500 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-purple-500 font-sans transition-all resize-none"
          />
          <p className="text-[11px] text-slate-500 font-mono">
            Describe flood, earthquake, cyclone, landslide, wildfire, or industrial emergency.
          </p>
        </div>

        {/* Analyze Situation Button */}
        <button
          type="submit"
          disabled={isProcessing}
          className="w-full py-4 rounded-xl bg-gradient-to-r from-cyan-600 via-blue-600 to-purple-600 hover:from-cyan-500 hover:via-blue-500 hover:to-purple-500 text-white font-bold text-sm shadow-xl shadow-cyan-500/20 transition-all duration-200 transform hover:-translate-y-0.5 flex items-center justify-center gap-2 font-mono uppercase tracking-wider disabled:opacity-50 cursor-pointer"
        >
          <Sparkles className="w-5 h-5 text-white" />
          <span>{isProcessing ? 'ANALYZING SITUATION WITH MULTI-AGENT AI...' : '[ ANALYZE SITUATION ]'}</span>
          <ArrowRight className="w-5 h-5" />
        </button>

      </form>

      {/* Suggested Location Example Pills */}
      <div className="mt-8 pt-6 border-t border-slate-800 space-y-3 relative z-10">
        <span className="text-xs font-mono text-slate-400 font-bold uppercase tracking-wider block">
          Quick Scenario Presets:
        </span>
        <div className="flex flex-wrap gap-2.5">
          <button
            onClick={() => handleQuickExample('Chennai, Tamil Nadu', 'Heavy flooding affecting multiple urban sectors with limited rescue vehicles and medical teams.')}
            className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-mono text-slate-300 hover:text-white transition-all cursor-pointer"
          >
            [ Chennai, Tamil Nadu ]
          </button>
          <button
            onClick={() => handleQuickExample('Mumbai, Maharashtra', 'Severe monsoon inundation in low-lying sectors with congested evacuation roads.')}
            className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-mono text-slate-300 hover:text-white transition-all cursor-pointer"
          >
            [ Mumbai, Maharashtra ]
          </button>
          <button
            onClick={() => handleQuickExample('Bengaluru, Karnataka', 'Flash flood emergency impacting residential districts with blocked road access.')}
            className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-mono text-slate-300 hover:text-white transition-all cursor-pointer"
          >
            [ Bengaluru, Karnataka ]
          </button>
          <button
            onClick={() => handleQuickExample('Kochi, Kerala', 'Coastal flood warning with urgent shelter and medic deployment requirements.')}
            className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-mono text-slate-300 hover:text-white transition-all cursor-pointer"
          >
            [ Kochi, Kerala ]
          </button>
        </div>
      </div>

    </div>
  );
}
