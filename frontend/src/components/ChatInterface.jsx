import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, Sparkles, MessageSquare, Zap, AlertTriangle } from 'lucide-react';
import ChatMessage from './ChatMessage';

export default function ChatInterface({
  chatHistory,
  onSendMessage,
  isProcessing,
  onActionClick
}) {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isProcessing]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim() || isProcessing) return;
    onSendMessage(inputText.trim());
    setInputText('');
  };

  const suggestedPrompts = [
    "Analyze Coimbatore",
    "Create emergency response plan",
    "We only have 3 rescue vehicles and 6 medics. Make a plan.",
    "A new critical emergency has appeared",
    "Why did you allocate resources this way?"
  ];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl glass-card flex flex-col h-[520px] relative overflow-hidden">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-purple-600/20 border border-purple-500/30 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-purple-400 animate-pulse" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              RESQ-AI Conversational Coordinator
            </h3>
            <p className="text-[11px] text-slate-400">Generative AI assistant with 7 active specialized agents</p>
          </div>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          🟢 Chat Session Active
        </span>
      </div>

      {/* Messages Scroll Feed */}
      <div className="flex-1 overflow-y-auto py-4 px-1 space-y-3 font-sans">
        {chatHistory && chatHistory.length > 0 ? (
          chatHistory.map((msg) => (
            <ChatMessage
              key={msg.id || Math.random()}
              message={msg}
              onActionClick={onActionClick}
            />
          ))
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 italic text-center px-4">
            <Bot className="w-10 h-10 text-purple-500/40 mb-2 animate-bounce" />
            <p className="text-sm font-semibold text-slate-300">Welcome to RESQ-AI Conversational Planning</p>
            <p className="text-xs text-slate-400 max-w-md mt-1">
              Ask questions, set resource bounds, or describe situational updates in natural language.
            </p>
          </div>
        )}

        {isProcessing && (
          <div className="flex items-center gap-2 text-xs text-purple-300 font-mono my-2 animate-pulse bg-purple-950/30 p-2.5 rounded-xl border border-purple-500/30 max-w-sm">
            <Sparkles className="w-4 h-4 text-purple-400 animate-spin" />
            <span>7 Specialized AI Agents reasoning...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Prompts Pills */}
      <div className="py-2 border-t border-slate-800/80 shrink-0 overflow-x-auto flex items-center gap-2">
        <span className="text-[10px] font-mono text-slate-500 shrink-0 font-bold uppercase">Quick Actions:</span>
        {suggestedPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => onSendMessage(prompt)}
            disabled={isProcessing}
            className="px-2.5 py-1 rounded-full bg-slate-800 hover:bg-slate-700 border border-slate-700 text-[11px] font-mono text-slate-300 hover:text-white shrink-0 transition-all cursor-pointer disabled:opacity-50"
          >
            [ {prompt} ]
          </button>
        ))}
      </div>

      {/* Message Input Box */}
      <form onSubmit={handleSubmit} className="mt-2 shrink-0 relative flex items-center">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ask a question or enter constraint e.g. 'We only have 3 rescue vehicles and 6 medics'..."
          disabled={isProcessing}
          className="w-full bg-slate-950/90 border border-slate-700 focus:border-purple-500 rounded-xl px-4 py-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-purple-500 font-sans pr-12 transition-all"
        />
        <button
          type="submit"
          disabled={!inputText.trim() || isProcessing}
          className="absolute right-2 p-2 rounded-lg bg-gradient-to-tr from-purple-600 to-indigo-600 text-white hover:from-purple-500 hover:to-indigo-500 transition-all disabled:opacity-40 cursor-pointer shadow-md"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>

    </div>
  );
}
