import React, { useState } from 'react';
import { User, Shield, BookOpen, ExternalLink, Tag, Users, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export function ProfilePage({ currentUser, onSwitchUser, allUsers }) {
  const [selectedUserId, setSelectedUserId] = useState(currentUser?.id || 1);

  const handleSelect = (e) => {
    const uId = parseInt(e.target.value);
    setSelectedUserId(uId);
    const targetUser = allUsers.find(u => u.id === uId);
    if (targetUser && onSwitchUser) {
      onSwitchUser(targetUser);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header & Quick Role Switcher */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <User className="w-5 h-5 text-amber-500" /> Researcher Profile & Role Switcher
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Switch between Student, Faculty, Researcher, and Admin profiles to test personalized feeds, recommendations, and permissions.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-600">Simulate Account:</span>
          <select
            value={currentUser?.id || 1}
            onChange={handleSelect}
            className="text-xs font-bold px-3 py-1.5 bg-amber-50 border border-amber-300 rounded-lg text-amber-950 focus:outline-none"
          >
            {allUsers.slice(0, 15).map(u => (
              <option key={u.id} value={u.id}>
                {u.full_name} ({u.role.toUpperCase()}) - {u.department}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Profile Card */}
      {currentUser && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-5">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-2xl bg-slate-900 text-amber-400 font-extrabold text-2xl flex items-center justify-center shrink-0 shadow-md">
              {currentUser.full_name?.charAt(0)}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-slate-900">{currentUser.full_name}</h2>
                <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                  currentUser.role === 'admin'
                    ? 'bg-rose-100 text-rose-800'
                    : currentUser.role === 'faculty'
                    ? 'bg-purple-100 text-purple-800'
                    : currentUser.role === 'researcher'
                    ? 'bg-indigo-100 text-indigo-800'
                    : 'bg-emerald-100 text-emerald-800'
                }`}>
                  {currentUser.role}
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">{currentUser.email} • {currentUser.department}</p>
              <p className="text-xs text-slate-700 mt-2 italic leading-relaxed">"{currentUser.bio}"</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-slate-100">
            <div>
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Research Interests</span>
              <p className="text-xs text-slate-800 leading-relaxed font-medium">{currentUser.research_interests}</p>
            </div>

            <div>
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Publications & Links</span>
              {currentUser.publication_url ? (
                <a
                  href={currentUser.publication_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-1.5"
                >
                  <ExternalLink className="w-3.5 h-3.5" /> View Google Scholar Profile
                </a>
              ) : (
                <span className="text-xs text-slate-400">None linked</span>
              )}
            </div>
          </div>

          {/* Research Interest Tags */}
          {currentUser.interest_tags && (
            <div className="pt-2 border-t border-slate-100">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">Topic Tags</span>
              <div className="flex flex-wrap gap-1.5">
                {currentUser.interest_tags.split(",").map((t, idx) => (
                  <span key={idx} className="px-2.5 py-1 bg-slate-100 text-slate-700 font-medium text-xs rounded-lg flex items-center gap-1">
                    <Tag className="w-3 h-3 text-slate-400" /> #{t.trim()}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Follow Stats */}
          <div className="flex items-center gap-6 pt-3 border-t border-slate-100 text-xs">
            <div>
              <strong className="text-slate-900 text-sm font-bold">{currentUser.followers_count || 12}</strong> <span className="text-slate-500">Followers</span>
            </div>
            <div>
              <strong className="text-slate-900 text-sm font-bold">{currentUser.following_count || 8}</strong> <span className="text-slate-500">Following</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
