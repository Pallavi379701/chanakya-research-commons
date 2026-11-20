import React, { useState, useEffect } from 'react';
import { 
  Search, BookOpen, MessageSquare, Bot, Sparkles, TrendingUp, 
  BarChart3, FlaskConical, User, Shield, GraduationCap, ChevronDown
} from 'lucide-react';
import { api } from './services/api';
import { SearchPage } from './pages/SearchPage';
import { FeedPage } from './pages/FeedPage';
import { LibraryPage } from './pages/LibraryPage';
import { AssistantPage } from './pages/AssistantPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { TrendsPage } from './pages/TrendsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { ProfilePage } from './pages/ProfilePage';

export default function App() {
  const [activeTab, setActiveTab] = useState('search');
  const [currentUser, setCurrentUser] = useState(null);
  const [allUsers, setAllUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function initUser() {
      try {
        const users = await api.getUsers('?limit=60');
        setAllUsers(users);
        if (users.length > 0) {
          // Default to first researcher/faculty
          setCurrentUser(users[0]);
        }
      } catch (err) {
        console.error("Init user error:", err);
      } finally {
        setLoading(false);
      }
    }
    initUser();
  }, []);

  const navItems = [
    { id: 'search', label: 'Unified Search', icon: Search, badge: 'F5' },
    { id: 'feed', label: 'Discussions', icon: MessageSquare, badge: 'F2' },
    { id: 'library', label: 'Library', icon: BookOpen, badge: 'F3' },
    { id: 'assistant', label: 'Research Assistant', icon: Bot, badge: 'F8' },
    { id: 'recommendations', label: 'Recommendations', icon: Sparkles, badge: 'F6' },
    { id: 'trends', label: 'Trends & Anomaly', icon: TrendingUp, badge: 'F7' },
    { id: 'analytics', label: 'Institutional Analytics', icon: BarChart3, badge: 'F9' },
    { id: 'evaluation', label: 'Evaluation Lab', icon: FlaskConical, badge: '40% Marks', highlight: true },
    { id: 'profile', label: 'Profile', icon: User, badge: 'F1' },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        <div className="text-center space-y-3">
          <GraduationCap className="w-12 h-12 text-amber-400 mx-auto animate-bounce" />
          <h2 className="text-lg font-bold">Chanakya Research Commons</h2>
          <p className="text-xs text-slate-400">Loading university data layer & mining engines...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top University Brand Bar */}
      <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo & University Name */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-amber-300 text-slate-950 flex items-center justify-center font-black text-lg shadow-md">
                <GraduationCap className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-base tracking-tight text-white">Chanakya Research Commons</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 font-semibold border border-amber-500/30">
                    Bangalore
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 hidden sm:block">
                  School of Engineering • Data Mining & Warehousing Mini-Project
                </p>
              </div>
            </div>

            {/* Role & Simulated User Switcher */}
            <div className="flex items-center gap-3">
              <div className="hidden md:flex items-center gap-2 bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-700 text-xs">
                <span className="text-slate-400 font-medium">Active Member:</span>
                <select
                  value={currentUser?.id || 1}
                  onChange={(e) => {
                    const u = allUsers.find(x => x.id === parseInt(e.target.value));
                    if (u) setCurrentUser(u);
                  }}
                  className="bg-transparent text-amber-400 font-bold focus:outline-none cursor-pointer"
                >
                  {allUsers.slice(0, 20).map(u => (
                    <option key={u.id} value={u.id} className="bg-slate-900 text-white">
                      {u.full_name} ({u.role.toUpperCase()}) - {u.department}
                    </option>
                  ))}
                </select>
              </div>

              <div className="w-8 h-8 rounded-full bg-amber-500 text-slate-950 font-extrabold text-xs flex items-center justify-center shadow-sm">
                {currentUser?.full_name?.charAt(0) || "U"}
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs Bar */}
        <div className="bg-slate-950/90 border-t border-slate-800/80 px-4 sm:px-6 lg:px-8 overflow-x-auto">
          <div className="max-w-7xl mx-auto flex items-center gap-1 py-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`px-3 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 whitespace-nowrap transition-all ${
                    isActive
                      ? 'bg-amber-500 text-slate-950 shadow-sm'
                      : item.highlight
                      ? 'text-amber-400 hover:bg-slate-800'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className={`text-[9px] px-1.5 py-0.2 rounded font-bold ${
                      isActive
                        ? 'bg-slate-950 text-amber-400'
                        : item.highlight
                        ? 'bg-amber-500/20 text-amber-300'
                        : 'bg-slate-800 text-slate-400'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'search' && <SearchPage currentUser={currentUser} />}
        {activeTab === 'feed' && <FeedPage currentUser={currentUser} />}
        {activeTab === 'library' && <LibraryPage currentUser={currentUser} />}
        {activeTab === 'assistant' && <AssistantPage />}
        {activeTab === 'recommendations' && <RecommendationsPage currentUser={currentUser} />}
        {activeTab === 'trends' && <TrendsPage currentUser={currentUser} />}
        {activeTab === 'analytics' && <AnalyticsPage />}
        {activeTab === 'evaluation' && <EvaluationPage />}
        {activeTab === 'profile' && (
          <ProfilePage 
            currentUser={currentUser} 
            onSwitchUser={setCurrentUser} 
            allUsers={allUsers}
            onUserRegistered={(u) => setAllUsers(prev => [u, ...prev])}
          />
        )}
      </main>

      {/* University Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-slate-500 text-xs text-center space-y-1">
        <p className="font-semibold text-slate-700">
          Chanakya Research Commons • Chanakya University, Bangalore
        </p>
        <p className="text-[11px] text-slate-400">
          Summative Assessment: Mini-Project | Data Mining and Warehousing (Course V Semester B.Tech, 2026-27)
        </p>
      </footer>
    </div>
  );
}
