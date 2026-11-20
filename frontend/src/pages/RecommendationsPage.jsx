import React, { useState, useEffect } from 'react';
import { Sparkles, Users, BookOpen, Bookmark, Check, ArrowRight, UserPlus, GitFork } from 'lucide-react';
import { api } from '../services/api';

export function RecommendationsPage({ currentUser }) {
  const [papers, setPapers] = useState([]);
  const [members, setMembers] = useState([]);
  const [coSavedSample, setCoSavedSample] = useState([]);
  const [loading, setLoading] = useState(true);
  const [savedIds, setSavedIds] = useState(new Set());
  const [followedIds, setFollowedIds] = useState(new Set());

  const loadRecommendations = async () => {
    setLoading(true);
    try {
      const [recPapers, recMembers] = await Promise.all([
        api.getRecommendedPapers(currentUser?.id || 1),
        api.getRecommendedMembers(currentUser?.id || 1)
      ]);
      setPapers(recPapers);
      setMembers(recMembers);

      // Fetch FP-Growth also-saved rules on first paper
      if (recPapers.length > 0) {
        const alsoSaved = await api.getAlsoSaved(recPapers[0].id);
        setCoSavedSample(alsoSaved);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecommendations();
  }, [currentUser]);

  const handleSave = async (paperId) => {
    try {
      await api.savePaper(paperId, "Saved from recommendations", "Reading List", currentUser?.id || 1);
      setSavedIds(prev => new Set([...prev, paperId]));
    } catch (err) {
      alert("Failed to save paper");
    }
  };

  const handleFollow = async (userId) => {
    try {
      await api.followUser(userId, currentUser?.id || 1);
      setFollowedIds(prev => new Set([...prev, userId]));
    } catch (err) {
      alert("Failed to follow member");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-500" /> Recommendations Hub
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Powered by Content-Based cosine profile matching, Collaborative Filtering, and FP-Growth Association Rule Mining.
          </p>
        </div>
        <div className="text-xs px-3 py-1.5 bg-amber-50 text-amber-900 border border-amber-200 rounded-lg font-medium">
          Active Profile: <strong className="text-slate-900">{currentUser?.full_name}</strong> ({currentUser?.department})
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Recommended Papers */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Papers You May Want to Read</h3>
                <p className="text-xs text-slate-500">Mined from your research interests, department priors, and peer saves</p>
              </div>
              <span className="text-xs font-semibold px-2.5 py-0.5 bg-amber-100 text-amber-900 rounded-full">
                {papers.length} Suggestions
              </span>
            </div>

            {loading ? (
              <div className="text-center py-8 text-slate-400 text-xs">Computing hybrid recommendations...</div>
            ) : papers.length === 0 ? (
              <p className="text-xs text-slate-400 text-center py-6">No paper recommendations available.</p>
            ) : (
              <div className="space-y-3">
                {papers.map((p) => (
                  <div key={p.id} className="p-3.5 rounded-xl border border-slate-100 hover:border-slate-300 transition-all space-y-2">
                    <div className="flex items-start justify-between gap-3">
                      <h4 className="text-xs font-bold text-slate-900 leading-snug">{p.title}</h4>
                      <button
                        onClick={() => handleSave(p.id)}
                        disabled={savedIds.has(p.id)}
                        className={`shrink-0 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all flex items-center gap-1 ${
                          savedIds.has(p.id)
                            ? 'bg-emerald-50 text-emerald-700'
                            : 'bg-slate-100 hover:bg-amber-100 hover:text-amber-800 text-slate-700'
                        }`}
                      >
                        {savedIds.has(p.id) ? <Check className="w-3.5 h-3.5" /> : <Bookmark className="w-3.5 h-3.5" />}
                        <span>{savedIds.has(p.id) ? "Saved" : "Save"}</span>
                      </button>
                    </div>

                    <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-500">
                      <span>{p.authors}</span>
                      <span>•</span>
                      <span className="font-medium text-slate-700">{p.department}</span>
                      <span>•</span>
                      <span>{p.venue} ({p.year})</span>
                      <span className="ml-auto text-amber-700 font-bold bg-amber-50 px-2 py-0.5 rounded">
                        Match Score: {p.recommendation_score}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* FP-Growth "Members Who Saved This Also Saved" */}
          {coSavedSample.length > 0 && (
            <div className="bg-amber-50/40 rounded-xl border border-amber-200/80 p-5 space-y-3">
              <div className="flex items-center gap-2">
                <GitFork className="w-4 h-4 text-amber-600" />
                <h3 className="text-xs font-bold text-amber-950 uppercase tracking-wider">
                  Association Rule Mining: "Members Who Saved This Also Saved"
                </h3>
              </div>
              <p className="text-xs text-slate-600">
                Generated via FP-Growth frequent itemset mining on campus library collections:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                {coSavedSample.map(item => (
                  <div key={item.id} className="p-3 bg-white rounded-lg border border-amber-100 text-xs space-y-1">
                    <h5 className="font-bold text-slate-900 text-[11px] line-clamp-1">{item.title}</h5>
                    <p className="text-[10px] text-slate-500">{item.authors} ({item.year}) • {item.department}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right 1 Col: Recommended Colleagues */}
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Researchers to Connect With</h3>
                <p className="text-xs text-slate-500">Shared research interests & co-saved literature</p>
              </div>
              <Users className="w-4 h-4 text-slate-400" />
            </div>

            {loading ? (
              <div className="text-center py-8 text-slate-400 text-xs">Matching researcher graph...</div>
            ) : members.length === 0 ? (
              <p className="text-xs text-slate-400 text-center py-6">No new colleague recommendations.</p>
            ) : (
              <div className="space-y-3">
                {members.map((u) => (
                  <div key={u.id} className="p-3 rounded-xl border border-slate-100 hover:border-slate-300 transition-all space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-slate-900 text-amber-400 font-bold text-xs flex items-center justify-center shrink-0">
                          {u.full_name.charAt(0)}
                        </div>
                        <div>
                          <h4 className="text-xs font-bold text-slate-900">{u.full_name}</h4>
                          <p className="text-[10px] text-slate-500">{u.role.toUpperCase()} • {u.department}</p>
                        </div>
                      </div>

                      <button
                        onClick={() => handleFollow(u.id)}
                        disabled={followedIds.has(u.id)}
                        className={`p-1.5 rounded-lg text-xs transition-all ${
                          followedIds.has(u.id)
                            ? 'bg-emerald-50 text-emerald-700'
                            : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                        }`}
                        title="Follow Member"
                      >
                        {followedIds.has(u.id) ? <Check className="w-3.5 h-3.5" /> : <UserPlus className="w-3.5 h-3.5" />}
                      </button>
                    </div>

                    <p className="text-[11px] text-slate-600 italic line-clamp-1">"{u.research_interests}"</p>

                    <div className="flex items-center justify-between text-[10px] pt-1 border-t border-slate-50">
                      <span className="text-slate-500">{u.shared_saved_count} shared papers saved</span>
                      <span className="text-emerald-700 font-bold bg-emerald-50 px-1.5 py-0.5 rounded">
                        {Math.round(u.match_score * 100)}% Match
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
