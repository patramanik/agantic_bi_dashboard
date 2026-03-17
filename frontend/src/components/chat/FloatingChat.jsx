import React, { useRef, useEffect } from 'react';
import { Send, MessageSquare, Loader2, X, ChevronRight, Upload } from 'lucide-react';
import QuickSuggestions from './QuickSuggestions';
import { getSuggestions } from '../../utils/api';

const FloatingChat = ({ 
  isChatOpen, 
  setIsChatOpen, 
  messages, 
  loading, 
  handleAction, 
  fileId,
  input,
  setInput,
  onUploadTrigger
}) => {
  const scrollRef = useRef(null);
  const [dynamicSuggestions, setDynamicSuggestions] = React.useState([]);
  const [isFetchingSuggestions, setIsFetchingSuggestions] = React.useState(false);

  useEffect(() => {
    if (fileId) {
      setIsFetchingSuggestions(true);
      getSuggestions(fileId)
        .then(res => setDynamicSuggestions(res.data))
        .catch(err => console.error("Failed to fetch suggestions:", err))
        .finally(() => setIsFetchingSuggestions(false));
    } else {
      setDynamicSuggestions([]);
      setIsFetchingSuggestions(false);
    }
  }, [fileId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [messages, loading]);

  return (
    <div className="fixed bottom-8 right-8 z-50 flex flex-col items-end gap-4">
      {/* Chat Window */}
      {isChatOpen && (
        <div className="w-[380px] max-w-[calc(100vw-2rem)] h-[600px] max-h-[calc(100vh-10rem)] glass-panel overflow-hidden flex flex-col shadow-3xl animate-slide-up border-indigo-500/20">
          {/* Chat Header */}
          <div className="px-5 py-4 bg-slate-900 flex justify-between items-center border-b border-white/5">
            <div className="flex items-center gap-2.5">
              <div className="relative">
                <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center shadow-lg">
                  <MessageSquare size={16} className="text-white" />
                </div>
                <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 border-2 border-slate-900 rounded-full" />
              </div>
              <div>
                <h4 className="text-[13px] font-bold text-white leading-tight">Analytic Intern</h4>
                <p className="text-[10px] text-emerald-400 font-bold uppercase tracking-widest">Processing</p>
              </div>
            </div>
            <button 
              onClick={() => setIsChatOpen(false)}
              className="p-1.5 hover:bg-white/10 rounded-lg text-slate-400 transition-colors"
            >
              <X size={18} />
            </button>
          </div>

          {/* Chat Body */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-5 flex flex-col gap-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'}>
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="chat-bubble-ai opacity-70 flex items-center gap-2">
                  <Loader2 size={14} className="animate-spin text-indigo-400" />
                  <span className="text-[11px] font-medium text-slate-400">Synthesizing...</span>
                </div>
              </div>
            )}
          </div>

          {/* Chat Footer */}
          <div className="p-4 bg-slate-900/50 border-top border-white/5">
            {isFetchingSuggestions ? (
              <div className="flex gap-2 items-center text-[11px] text-slate-400 font-medium animate-pulse mb-3">
                <Loader2 size={12} className="animate-spin text-indigo-400" />
                Generating neural prompts...
              </div>
            ) : (
              fileId && <QuickSuggestions onSelect={handleAction} disabled={loading} suggestions={dynamicSuggestions} />
            )}
            <div className="mt-3 flex gap-2">
              <button 
                onClick={onUploadTrigger}
                className="p-2.5 bg-slate-800 hover:bg-slate-700 text-indigo-400 rounded-xl transition-all border border-white/5 active:scale-95"
                title="Upload Source"
              >
                <Upload size={18} />
              </button>
              <input 
                type="text" 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                placeholder={fileId ? "Enter request..." : "Connect data first..."}
                className="flex-1 bg-black/40 border border-white/10 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-indigo-500/50 transition-colors"
                disabled={!fileId && messages.length > 0 && messages[0].role === 'ai' && messages[0].content.includes('Connect your data')} // Allow input if no data yet? Actually, the user can only use chat if data is connected based on handleAction logic.
              />
              <button 
                onClick={() => handleAction(input)}
                disabled={!fileId || loading || !input.trim()}
                className="p-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl transition-all shadow-md active:scale-95"
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* FAB */}
      <button 
        onClick={() => setIsChatOpen(!isChatOpen)}
        className={`w-14 h-14 rounded-2xl flex items-center justify-center shadow-2xl transition-all duration-500 active:scale-90 ${isChatOpen ? 'bg-slate-800 rotate-90' : 'bg-indigo-600 hover:bg-indigo-500 shadow-indigo-600/30'}`}
      >
        {isChatOpen ? <ChevronRight className="text-white" size={24} /> : <MessageSquare className="text-white" size={24} />}
        {!isChatOpen && messages.length > 0 && !fileId && (
           <div className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full border-2 border-[#020617] animate-pulse" />
        )}
      </button>
    </div>
  );
};

export default FloatingChat;
