import React, { useState } from 'react';
import { Search, BookOpen, Users, MessageSquare, Globe, ExternalLink, Bookmark, Check, Sparkles, Filter } from 'lucide-react';
import { api } from '../services/api';

export function SearchPage({ currentUser, onSavePaper }) {
  const [query, setQuery] = useState('transformer');
  const [mode, setMode] = useState('hybrid');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [savedIds, setSavedIds] = useState(new Set());

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data = await api.search(query, mode, currentUser?.id || 1);
      setResults(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (paperId) => {
    try {
      await api.savePaper(paperId, "Saved from search", "Reading List", currentUser?.id || 1);
      setSavedIds(prev => new Set([...prev, paperId]));
      if (onSavePaper) onSavePaper();
    } catch (err) {
      alert("Failed to save paper");
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-2xl shadow-sm border border-slate-800">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 text-xs font-medium mb-3">
            <Sparkles className="w-3.5 h-3.5" /> F5: Unified 4-Panel Federated Search
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Unified Research Search</h1>
          <p className="text-slate-300 text-sm mt-1">
            Search external scholarly sources, Chanakya library collections, faculty researchers, and campus discussions in one single view.
          </p>

          {/* Search Input & Mode Selector */}
          <form onSubmit={handleSearch} className="mt-5 space-y-3">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search papers, algorithms, faculty, research topics (e.g. 'transformer', 'consensus', 'crispr')..."
                  className="w-full pl-11 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-400 text-sm"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 bg-amber-500 hover:bg-amber-600 text-slate-950 font-semibold rounded-xl text-sm transition-all shadow-md flex items-center gap-2"
              >
                {loading ? "Searching..." : "Search All"}
              </button>
            </div>

            {/* Search Mode Toggles */}
            <div className="flex items-center gap-4 text-xs">
              <span className="text-slate-400 font-medium">Search Mode:</span>
              <label className="flex items-center gap-1.5 cursor-pointer text-slate-300 hover:text-white">
                <input
                  type="radio"
                  name="searchMode"
                  value="hybrid"
                  checked={mode === 'hybrid'}
                  onChange={() => setMode('hybrid')}
                  className="text-amber-500 focus:ring-0"
                />
                <span className="font-semibold text-amber-400">Hybrid (Semantic + Keyword + PageRank)</span>
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer text-slate-300 hover:text-white">
                <input
                  type="radio"
                  name="searchMode"
                  value="semantic"
                  checked={mode === 'semantic'}
                  onChange={() => setMode('semantic')}
                  className="text-amber-500 focus:ring-0"
                />
                <span>Semantic Vector Embeddings</span>
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer text-slate-300 hover:text-white">
                <input
                  type="radio"
                  name="searchMode"
                  value="keyword"
                  checked={mode === 'keyword'}
                  onChange={() => setMode('keyword')}
                  className="text-amber-500 focus:ring-0"
                />
                <span>BM25 Lexical Keyword</span>
              </label>
            </div>
          </form>
        </div>
      </div>

      {/* Results Header */}
      {results && (
        <div className="flex items-center justify-between border-b border-slate-200 pb-3">
          <div className="text-sm text-slate-600">
            Found <strong className="text-slate-900">{results.total_matches}</strong> matches for "<span className="italic">{results.query}</span>" ({results.mode} mode)
          </div>

          {/* Result Filter Tabs */}
          <div className="flex gap-2">
            {[
              { id: 'all', label: 'All 4 Panels', count: results.total_matches },
              { id: 'external', label: 'External Scholarly', count: results.external_papers.length, icon: Globe },
              { id: 'library', label: 'Chanakya Library', count: results.chanakya_library.length, icon: BookOpen },
              { id: 'people', label: 'Researchers', count: results.people.length, icon: Users },
              { id: 'posts', label: 'Discussions', count: results.posts.length, icon: MessageSquare },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1.5 text-xs font-medium rounded-lg flex items-center gap-1.5 transition-all ${
                  activeTab === tab.id
                    ? 'bg-slate-900 text-white'
                    : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
                }`}
              >
                {tab.icon && <tab.icon className="w-3.5 h-3.5" />}
                {tab.label}
                <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${activeTab === tab.id ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-700'}`}>
                  {tab.count}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 4-Panel Grid */}
      {results && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* PANEL 1: External Scholarly Papers */}
          {(activeTab === 'all' || activeTab === 'external') && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-blue-50 text-blue-600 rounded-lg">
                    <Globe className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900 text-sm">1. External Scholarly Sources</h3>
                    <p className="text-xs text-slate-500">Fetched via arXiv, OpenAlex & Semantic Scholar</p>
                  </div>
                </div>
                <span className="text-xs font-semibold px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">
                  {results.external_papers.length} Papers
                </span>
              </div>

              {results.external_papers.length === 0 ? (
                <p className="text-xs text-slate-400 py-4 text-center">No external papers matched.</p>
              ) : (
                <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
                  {results.external_papers.map((p) => (
                    <div key={p.id} className="p-3.5 rounded-lg border border-slate-100 hover:border-slate-300 hover:bg-slate-50/50 transition-all space-y-2">
                      <div className="flex items-start justify-between gap-3">
                        <h4 className="text-xs font-bold text-slate-900 leading-snug">{p.title}</h4>
                        <button
                          onClick={() => handleSave(p.id)}
                          disabled={savedIds.has(p.id)}
                          className={`shrink-0 p-1.5 rounded-lg text-xs transition-all flex items-center gap-1 ${
                            savedIds.has(p.id)
                              ? 'bg-emerald-50 text-emerald-700'
                              : 'bg-slate-100 hover:bg-amber-100 hover:text-amber-800 text-slate-700'
                          }`}
                          title="Save to Library"
                        >
                          {savedIds.has(p.id) ? <Check className="w-3.5 h-3.5" /> : <Bookmark className="w-3.5 h-3.5" />}
                          <span>{savedIds.has(p.id) ? "Saved" : "Save"}</span>
                        </button>
                      </div>

                      <p className="text-[11px] text-slate-600 line-clamp-2">{p.abstract}</p>

                      <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-500 pt-1">
                        <span>{p.authors}</span>
                        <span>•</span>
                        <span className="font-medium text-slate-700">{p.venue} ({p.year})</span>
                        <span>•</span>
                        {/* Deduplication merged sources badge */}
                        <div className="flex items-center gap-1">
                          {p.sources && p.sources.map(src => (
                            <span key={src} className="px-1.5 py-0.5 bg-slate-200 text-slate-700 rounded font-medium">
                              {src}
                            </span>
                          ))}
                        </div>
                        {p.pagerank_score > 0 && (
                          <span className="ml-auto text-indigo-600 font-semibold bg-indigo-50 px-1.5 py-0.5 rounded">
                            PR: {p.pagerank_score}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* PANEL 2: Chanakya University Library */}
          {(activeTab === 'all' || activeTab === 'library') && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-amber-50 text-amber-600 rounded-lg">
                    <BookOpen className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900 text-sm">2. Chanakya University Library</h3>
                    <p className="text-xs text-slate-500">Items already saved by university researchers</p>
                  </div>
                </div>
                <span className="text-xs font-semibold px-2 py-0.5 bg-amber-100 text-amber-800 rounded-full">
                  {results.chanakya_library.length} Items
                </span>
              </div>

              {results.chanakya_library.length === 0 ? (
                <p className="text-xs text-slate-400 py-4 text-center">No library items saved for this topic yet.</p>
              ) : (
                <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
                  {results.chanakya_library.map((p) => (
                    <div key={p.id} className="p-3.5 rounded-lg border border-amber-100 bg-amber-50/20 hover:border-amber-300 transition-all space-y-2">
                      <div className="flex items-start justify-between gap-3">
                        <h4 className="text-xs font-bold text-slate-900 leading-snug">{p.title}</h4>
                        <span className="shrink-0 px-2 py-0.5 bg-amber-100 text-amber-800 text-[11px] font-semibold rounded-full flex items-center gap-1">
                          <Bookmark className="w-3 h-3" /> {p.save_count} saved
                        </span>
                      </div>

                      <p className="text-[11px] text-slate-600 line-clamp-2">{p.abstract}</p>

                      <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-500 pt-1">
                        <span>{p.authors}</span>
                        <span>•</span>
                        <span className="font-medium text-slate-700">{p.department}</span>
                        <span className="ml-auto text-amber-700 font-semibold bg-amber-100/70 px-1.5 py-0.5 rounded">
                          {p.citation_count} citations
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* PANEL 3: University Members / Researchers */}
          {(activeTab === 'all' || activeTab === 'people') && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-emerald-50 text-emerald-600 rounded-lg">
                    <Users className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900 text-sm">3. Faculty & Student Researchers</h3>
                    <p className="text-xs text-slate-500">Colleagues active in this research area</p>
                  </div>
                </div>
                <span className="text-xs font-semibold px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full">
                  {results.people.length} Members
                </span>
              </div>

              {results.people.length === 0 ? (
                <p className="text-xs text-slate-400 py-4 text-center">No matching researchers found.</p>
              ) : (
                <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
                  {results.people.map((u) => (
                    <div key={u.id} className="p-3 rounded-lg border border-slate-100 hover:border-slate-300 transition-all flex items-start gap-3">
                      <div className="w-9 h-9 rounded-full bg-slate-800 text-amber-400 flex items-center justify-center font-bold text-xs shrink-0">
                        {u.full_name.charAt(0)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h4 className="text-xs font-bold text-slate-900 truncate">{u.full_name}</h4>
                          <span className="text-[10px] px-2 py-0.5 rounded-full capitalize bg-slate-100 text-slate-700 font-medium">
                            {u.role}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500">{u.department}</p>
                        <p className="text-[11px] text-slate-700 mt-1 line-clamp-1 italic">"{u.research_interests}"</p>
                        {u.interest_tags && (
                          <div className="flex flex-wrap gap-1 mt-1.5">
                            {u.interest_tags.split(",").slice(0, 3).map((tag, i) => (
                              <span key={i} className="px-1.5 py-0.2 bg-slate-100 text-slate-600 text-[10px] rounded">
                                {tag.trim()}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* PANEL 4: Related Discussions & Posts */}
          {(activeTab === 'all' || activeTab === 'posts') && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-purple-50 text-purple-600 rounded-lg">
                    <MessageSquare className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900 text-sm">4. Campus Discussions & Posts</h3>
                    <p className="text-xs text-slate-500">Peer debates, questions, and seminar notes</p>
                  </div>
                </div>
                <span className="text-xs font-semibold px-2 py-0.5 bg-purple-100 text-purple-800 rounded-full">
                  {results.posts.length} Posts
                </span>
              </div>

              {results.posts.length === 0 ? (
                <p className="text-xs text-slate-400 py-4 text-center">No discussion threads on this topic yet.</p>
              ) : (
                <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
                  {results.posts.map((post) => (
                    <div key={post.id} className="p-3.5 rounded-lg border border-slate-100 hover:border-slate-300 transition-all space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] text-slate-500 font-medium">By {post.author_name} ({post.department})</span>
                        <span className="text-[10px] px-2 py-0.5 bg-purple-50 text-purple-700 font-semibold rounded">
                          ▲ {post.upvotes} upvotes
                        </span>
                      </div>
                      <h4 className="text-xs font-bold text-slate-900">{post.title}</h4>
                      <p className="text-[11px] text-slate-600 line-clamp-2">{post.content}</p>
                      <div className="flex items-center gap-1 text-[10px] text-slate-500 pt-1">
                        <span className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">{post.tags}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
