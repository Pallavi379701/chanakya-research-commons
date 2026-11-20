import React, { useState } from 'react';
import { Bot, Send, BookOpen, ExternalLink, CheckCircle, Sparkles, ShieldCheck, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../services/api';

export function AssistantPage() {
  const [question, setQuestion] = useState('How does attention reduce computational overhead in transformers?');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedCitations, setExpandedCitations] = useState({});

  const handleAsk = async (e) => {
    if (e) e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);

    const userQ = question;
    setQuestion('');
    try {
      const response = await api.askAssistant(userQ);
      setHistory(prev => [...prev, {
        question: userQ,
        answer: response.answer,
        citations: response.citations,
        timestamp: new Date().toLocaleTimeString()
      }]);
    } catch (err) {
      alert("Failed to get answer from research assistant");
    } finally {
      setLoading(false);
    }
  };

  const toggleCitation = (idx) => {
    setExpandedCitations(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-2xl border border-slate-800 shadow-sm">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 text-xs font-medium mb-3">
          <Bot className="w-3.5 h-3.5" /> F8: Retrieval-Augmented Generation (RAG)
        </div>
        <h1 className="text-2xl font-bold tracking-tight">Grounded Research Assistant</h1>
        <p className="text-slate-300 text-sm mt-1">
          Ask questions in natural language. Every answer is strictly grounded in Chanakya University's scholarly papers and library holdings with verifiable citations.
        </p>
      </div>

      {/* Suggested Prompts */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="text-slate-400 font-medium">Try asking:</span>
        {[
          "What is self-attention in multimodal transformers?",
          "How does Raft consensus handle network partitions?",
          "How do high-fidelity Cas12a nucleases prevent off-target edits?",
          "What is Ring-LWE lattice cryptography security?"
        ].map((q, i) => (
          <button
            key={i}
            onClick={() => setQuestion(q)}
            className="px-2.5 py-1 bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 rounded-lg transition-all"
          >
            "{q.slice(0, 35)}..."
          </button>
        ))}
      </div>

      {/* Query Input Box */}
      <form onSubmit={handleAsk} className="flex gap-2 bg-white p-2 rounded-xl border border-slate-200 shadow-sm">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask any research question grounded in university papers..."
          className="flex-1 px-4 py-2.5 text-xs bg-transparent focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="px-5 py-2.5 bg-amber-500 hover:bg-amber-600 disabled:bg-slate-200 text-slate-950 font-bold rounded-lg text-xs transition-all shadow-sm flex items-center gap-1.5"
        >
          <Send className="w-3.5 h-3.5" /> {loading ? "Retrieving & Synthesizing..." : "Ask Assistant"}
        </button>
      </form>

      {/* Conversational Answers Stream */}
      <div className="space-y-6">
        {history.map((turn, tIdx) => (
          <div key={tIdx} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
            {/* Question */}
            <div className="flex items-start gap-3">
              <div className="w-7 h-7 rounded-full bg-slate-900 text-amber-400 font-bold text-xs flex items-center justify-center shrink-0">
                Q
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">{turn.question}</h3>
                <span className="text-[10px] text-slate-400">{turn.timestamp}</span>
              </div>
            </div>

            {/* Grounded Answer */}
            <div className="flex items-start gap-3 pl-1">
              <div className="w-7 h-7 rounded-full bg-amber-100 text-amber-800 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                <Bot className="w-4 h-4 text-amber-600" />
              </div>
              <div className="flex-1 space-y-3">
                <div className="text-xs text-slate-800 leading-relaxed whitespace-pre-line bg-slate-50/80 p-4 rounded-xl border border-slate-100">
                  {turn.answer}
                </div>

                {/* Grounding Passages Accordion */}
                {turn.citations && turn.citations.length > 0 && (
                  <div className="space-y-2 pt-2">
                    <div className="flex items-center justify-between text-xs text-slate-500 font-semibold px-1">
                      <span className="flex items-center gap-1.5 text-emerald-700">
                        <ShieldCheck className="w-4 h-4 text-emerald-600" /> Verifiable Retrieved Passages ({turn.citations.length} Citations)
                      </span>
                      <span className="text-[10px] text-slate-400">Click to inspect source text excerpts</span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {turn.citations.map((c, cIdx) => (
                        <div key={cIdx} className="p-3 bg-white rounded-xl border border-slate-200 hover:border-slate-300 transition-all text-xs space-y-2">
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex items-center gap-1.5">
                              <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold flex items-center justify-center">
                                [{c.citation_index}]
                              </span>
                              <h4 className="font-bold text-slate-900 text-[11px] leading-snug line-clamp-1">{c.title}</h4>
                            </div>
                            <span className="text-[10px] text-slate-400 font-mono">Score: {c.score}</span>
                          </div>

                          <div className="text-[10px] text-slate-500">{c.authors}</div>

                          <div className="p-2 bg-slate-50 rounded-lg text-[11px] text-slate-700 italic border-l-2 border-emerald-500">
                            "{c.passage}"
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
