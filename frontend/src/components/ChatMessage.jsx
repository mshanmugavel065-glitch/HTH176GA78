import React from 'react';
import { Bot, User, Brain, ShieldAlert, CheckCircle2 } from 'lucide-react';

export default function ChatMessage({ message, onActionClick }) {
  const isUser = message.sender === 'user';

  // Basic format markdown bolding and linebreaks
  const renderFormattedText = (text) => {
    if (!text) return '';
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      // Replace **text** with <strong>
      const parts = line.split(/(\*\*.*?\*\*)/g);
      return (
        <div key={idx} className={line.trim() === '' ? 'h-2' : 'my-0.5'}>
          {parts.map((part, pIdx) => {
            if (part.startsWith && part.startsWith('**') && part.endsWith('**')) {
              return <strong key={pIdx} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
            } else if (part.startsWith('**') && part.endsWith('**')) {
              return <strong key={pIdx} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
            }
            return part;
          })}
        </div>
      );
    });
  };

  return (
    <div className={`flex gap-3 my-3 font-sans ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-md ${
        isUser
          ? 'bg-gradient-to-tr from-cyan-600 to-blue-600 text-white'
          : 'bg-gradient-to-tr from-purple-600 to-indigo-600 text-white'
      }`}>
        {isUser ? <User className="w-4 h-4" /> : <Brain className="w-4 h-4" />}
      </div>

      {/* Bubble Content */}
      <div className={`max-w-2xl rounded-2xl p-4 text-xs leading-relaxed ${
        isUser
          ? 'bg-cyan-600/20 border border-cyan-500/40 text-cyan-100 rounded-tr-none'
          : 'bg-slate-900/90 border border-slate-800 text-slate-200 glass-card rounded-tl-none'
      }`}>
        
        {/* Header Sender Info */}
        <div className="flex items-center justify-between gap-4 mb-1.5 pb-1 border-b border-slate-800/60 font-mono text-[10px]">
          <span className={`font-bold ${isUser ? 'text-cyan-300' : 'text-purple-300 flex items-center gap-1'}`}>
            {!isUser && <ShieldAlert className="w-3 h-3 text-purple-400" />}
            {message.agent_name || (isUser ? 'You' : 'RESQ-AI Assistant')}
          </span>
          <span className="text-slate-500">{message.timestamp}</span>
        </div>

        {/* Formatted Message Body */}
        <div className="text-slate-200">
          {renderFormattedText(message.content)}
        </div>

        {/* Interactive Action Buttons */}
        {!isUser && message.suggested_actions && message.suggested_actions.length > 0 && (
          <div className="mt-3 pt-2.5 border-t border-slate-800 flex flex-wrap gap-2">
            {message.suggested_actions.map((act, idx) => (
              <button
                key={idx}
                onClick={() => onActionClick && onActionClick(act)}
                className="px-2.5 py-1 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-[11px] font-mono font-medium text-purple-300 hover:text-white transition-all transform hover:-translate-y-0.5 cursor-pointer"
              >
                [ {act} ]
              </button>
            ))}
          </div>
        )}

      </div>

    </div>
  );
}
