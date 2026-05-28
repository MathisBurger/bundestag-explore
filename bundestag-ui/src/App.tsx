import React, { useState, useRef, useEffect } from 'react';
import type {Message, Citation, ChatRequest} from './types.ts';
import { MessageSquare, Send, Sparkles, User, Landmark, BookOpen, Layers } from 'lucide-react';

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [selectedParty, setSelectedParty] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeCitations, setActiveCitations] = useState<Citation[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userQuery = input;
    setInput('');

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: userQuery
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const apiUrl = (window as any)._env_.API_URL;
      const response = await fetch(`${apiUrl}/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userQuery,
          party: selectedParty,
        } as ChatRequest)
      });

      if (!response.ok) throw new Error('Backend-Fehler');

      const data = await response.json();

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.answer,
        citations: data.citations
      };

      setMessages(prev => [...prev, assistantMessage]);
      if (data.citations && data.citations.length > 0) {
        setActiveCitations(data.citations);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '❌ Fehler: Das Quarkus-Backend konnte nicht erreicht werden.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen bg-slate-900 text-slate-100 font-sans overflow-hidden">

      {/* LINKER BEREICH: Chat & Filter */}
      <div className="flex flex-col flex-1 h-full border-r border-slate-800">

        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 bg-slate-900/50 backdrop-blur-md border-b border-slate-800">
          <div className="flex items-center gap-3">
            <Landmark className="w-6 h-6 text-emerald-400" />
            <h1 className="text-xl font-bold tracking-wide">Bundestag <span className="text-emerald-400">Explore AI</span></h1>
          </div>

          {/* Controls: Provider & Fraktion */}
          <div className="flex items-center gap-4">
            <select
              value={selectedParty || ''}
              onChange={(e) => setSelectedParty(e.target.value ? e.target.value : null)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm font-medium focus:outline-none focus:border-emerald-500 transition"
            >
              <option value="">Alle Fraktionen</option>
              <option value="SPD">SPD</option>
              <option value="CDU/CSU">CDU/CSU</option>
              <option value="GRÜNE">BÜNDNIS 90/DIE GRÜNEN</option>
              <option value="FDP">FDP</option>
              <option value="AfD">AfD</option>
              <option value="Linke">Die Linke</option>
            </select>
          </div>
        </header>

        {/* Chat-Verlauf */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-slate-800">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-3">
              <MessageSquare className="w-12 h-12 stroke-[1.5]" />
              <p className="text-lg">Stelle eine Frage zu den Plenarsitzungen...</p>
              <p className="text-xs bg-slate-800 px-3 py-1.5 rounded-full border border-slate-700/50">
                Beispiel: "Wer hat sich am kritischsten zur Rentenreform geäußert?"
              </p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-4 max-w-3xl ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
              >
                {/* Avatar */}
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-lg ${
                  msg.role === 'user' ? 'bg-emerald-500 text-white' : 'bg-slate-800 text-emerald-400 border border-slate-700'
                }`}>
                  {msg.role === 'user' ? <User className="w-5 h-5" /> : <Sparkles className="w-5 h-5" />}
                </div>

                {/* Message Bubble */}
                <div className="space-y-2">
                  <div className={`px-5 py-3.5 rounded-2xl shadow-md text-[15px] leading-relaxed ${
                    msg.role === 'user' 
                      ? 'bg-emerald-600 text-white rounded-tr-none' 
                      : 'bg-slate-800/80 border border-slate-700/60 rounded-tl-none text-slate-200'
                  }`}>
                    {msg.content}
                  </div>

                  {/* Klickbarer Quellen-Indikator unter der KI-Antwort */}
                  {msg.role === 'assistant' && msg.citations && msg.citations.length > 0 && (
                    <button
                      onClick={() => setActiveCitations(msg.citations || [])}
                      className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1.5 px-1 py-0.5 transition"
                    >
                      <BookOpen className="w-3.5 h-3.5" />
                      {msg.citations.length} Belege aus Qdrant geladen
                    </button>
                  )}
                </div>
              </div>
            ))
          )}

          {/* Loading Animation */}
          {isLoading && (
            <div className="flex gap-4 mr-auto">
              <div className="w-9 h-9 rounded-xl bg-slate-800 text-emerald-400 border border-slate-700 flex items-center justify-center animate-pulse">
                <Sparkles className="w-5 h-5" />
              </div>
              <div className="bg-slate-800/40 border border-slate-700/40 px-5 py-3.5 rounded-2xl rounded-tl-none flex items-center gap-2 text-slate-400 text-sm">
                <span className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                <span className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                <span className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                Durchsuche Parlamentsdatenbank...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <footer className="p-4 bg-slate-900 border-t border-slate-800">
          <form onSubmit={handleSend} className="relative max-w-4xl mx-auto flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={selectedParty ? `Frage an die ${selectedParty} Fraktion...` : "Frag das Parlament..."}
              className="w-full bg-slate-800/90 border border-slate-700 hover:border-slate-600 focus:border-emerald-500 rounded-xl pl-5 pr-14 py-3.5 text-slate-100 placeholder-slate-500 shadow-inner focus:outline-none transition"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-2.5 p-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 disabled:bg-slate-700 disabled:text-slate-500 text-slate-950 font-bold transition shadow-md"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </footer>
      </div>

      {/* RECHTER BEREICH: Das Quellen-Inspector-Panel */}
      <div className="w-96 h-full bg-slate-950/60 backdrop-blur-lg flex flex-col">
        <div className="px-6 py-5 border-b border-slate-800 flex items-center gap-2.5">
          <Layers className="w-5 h-5 text-emerald-400" />
          <h2 className="font-bold tracking-wide">Zitate</h2>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4 style-scrollbar">
          {activeCitations.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-600 text-center p-4">
              <BookOpen className="w-8 h-8 mb-2 stroke-[1.5]" />
              <p className="text-sm">Sobald du eine Frage stellst, siehst du hier die exakten Belege aus den Plenarsegmenten.</p>
            </div>
          ) : (
            activeCitations.map((cite, index) => (
              <div
                key={index}
                className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl space-y-2 hover:border-slate-700/60 transition shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-slate-200 truncate max-w-[180px]">
                    {cite.speaker}
                  </span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-md font-extrabold uppercase border ${
                    cite.party === 'SPD' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                    cite.party === 'CDU/CSU' ? 'bg-slate-700/30 text-slate-300 border-slate-600/30' :
                    cite.party === 'GRÜNE' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
                    cite.party === 'FDP' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                    'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  }`}>
                    {cite.party}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 font-medium line-clamp-1 border-b border-slate-800/60 pb-1.5">
                  TOP: {cite.topic}
                </div>
                <p className="text-xs text-slate-400 italic leading-relaxed pt-1">
                  {cite.text}
                </p>
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  );
}