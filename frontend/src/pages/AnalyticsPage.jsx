import React, { useState, useEffect } from 'react';
import { BarChart3, Network, Database, Layers, ArrowDown, ChevronRight, Award, Building2, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export function AnalyticsPage() {
  const [trends, setTrends] = useState([]);
  const [collaboration, setCollaboration] = useState(null);
  const [topPapers, setTopPapers] = useState([]);
  const [drilldown, setDrilldown] = useState(null);
  const [selectedDept, setSelectedDept] = useState("Computer Science");
  const [loading, setLoading] = useState(true);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const results = await Promise.allSettled([
        api.getDepartmentTrends(),
        api.getCollaborationNetwork(),
        api.getTopEngagedPapers(),
        api.getDrilldown(selectedDept)
      ]);
      if (results[0].status === 'fulfilled' && results[0].value) setTrends(results[0].value);
      if (results[1].status === 'fulfilled' && results[1].value) setCollaboration(results[1].value);
      if (results[2].status === 'fulfilled' && results[2].value) setTopPapers(results[2].value);
      if (results[3].status === 'fulfilled' && results[3].value) setDrilldown(results[3].value);
    } catch (err) {
      console.error("Error loading analytics:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, [selectedDept]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-2xl border border-slate-800 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 text-xs font-medium mb-3">
            <Database className="w-3.5 h-3.5" /> F9: Institutional Analytics Warehouse
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Institutional Research Analytics</h1>
          <p className="text-slate-300 text-sm mt-1">
            Columnar OLAP queries powered by DuckDB over Star Schema Parquet files (Gold Layer).
          </p>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={loadAnalytics}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-amber-400' : ''}`} />
            {loading ? 'Querying DuckDB...' : 'Refresh OLAP'}
          </button>
          <div className="text-right">
            <span className="text-[10px] text-slate-400 block uppercase tracking-wider font-semibold">Engine</span>
            <span className="text-sm font-bold text-amber-400 font-mono">DuckDB 2.0 / Parquet Star Schema</span>
          </div>
        </div>
      </div>

      {/* Sleep / Cold Start Notice Banner if backend hasn't responded */}
      {!drilldown && !loading && (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 p-4 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm">
          <div>
            <p className="font-bold text-sm">Analytics Engine Initializing</p>
            <p className="text-xs text-amber-700 mt-0.5">
              Render free tier instances sleep after inactivity. If the service is waking up, please wait 15-20 seconds and click Retry.
            </p>
          </div>
          <button
            onClick={loadAnalytics}
            className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-lg transition-colors shrink-0"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* KPI Summary Cards */}
      {drilldown?.university_summary && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
          {[
            { label: "Active Researchers", val: drilldown.university_summary.total_researchers, color: "text-blue-600", bg: "bg-blue-50" },
            { label: "Catalog Papers", val: drilldown.university_summary.total_papers, color: "text-amber-600", bg: "bg-amber-50" },
            { label: "Library Saves", val: drilldown.university_summary.total_library_saves, color: "text-emerald-600", bg: "bg-emerald-50" },
            { label: "Discussions", val: drilldown.university_summary.total_discussions, color: "text-purple-600", bg: "bg-purple-50" },
            { label: "Warehouse Events", val: drilldown.university_summary.total_warehouse_events, color: "text-slate-800", bg: "bg-slate-100" },
          ].map((kpi, idx) => (
            <div key={idx} className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block">{kpi.label}</span>
              <span className={`text-xl font-extrabold ${kpi.color}`}>{kpi.val?.toLocaleString()}</span>
            </div>
          ))}
        </div>
      )}

      {/* CROSS-DEPARTMENT COLLABORATION NETWORK */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <Network className="w-5 h-5 text-indigo-600" />
            <div>
              <h3 className="text-sm font-bold text-slate-900">Inter-Departmental Collaboration Network</h3>
              <p className="text-xs text-slate-500">Cross-department citation flows and interdisciplinary co-work matrix</p>
            </div>
          </div>
          <span className="text-xs bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full font-bold">
            {collaboration?.links?.length || 0} Cross-Dept Citation Flows
          </span>
        </div>

        {/* Visual Graph Representation */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Department Nodes */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">Department Nodes</h4>
            <div className="grid grid-cols-2 gap-2">
              {collaboration?.nodes?.map((node, i) => (
                <div
                  key={node.id}
                  onClick={() => setSelectedDept(node.name)}
                  className={`p-3 rounded-lg border text-xs cursor-pointer transition-all ${
                    selectedDept === node.name
                      ? 'bg-indigo-50 border-indigo-300 font-bold text-indigo-950 shadow-sm'
                      : 'bg-slate-50 border-slate-100 hover:bg-slate-100 text-slate-700'
                  }`}
                >
                  <Building2 className="w-3.5 h-3.5 mb-1 text-indigo-500" />
                  <div className="leading-snug">{node.name}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Cross-Department Flows */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">Top Interdisciplinary Flows</h4>
            <div className="space-y-1.5 max-h-[220px] overflow-y-auto pr-1">
              {collaboration?.links?.slice(0, 7).map((link, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-slate-800 text-[11px]">
                    <span className="font-semibold text-slate-900">{link.source}</span>
                    <span className="text-slate-400">➔</span>
                    <span className="font-semibold text-slate-900">{link.target}</span>
                  </div>
                  <span className="font-bold text-indigo-700 bg-indigo-100/70 px-2 py-0.5 rounded text-[10px]">
                    {link.weight} Citations
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 4-LEVEL HIERARCHICAL DRILL-DOWN */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-amber-600" />
            <div>
              <h3 className="text-sm font-bold text-slate-900">4-Level Hierarchical Analytics Drilldown</h3>
              <p className="text-xs text-slate-500">University ➔ Department ➔ Topic ➔ Member</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Selected:</span>
            <select
              value={selectedDept}
              onChange={(e) => setSelectedDept(e.target.value)}
              className="text-xs font-bold px-3 py-1.5 bg-slate-100 border border-slate-200 rounded-lg focus:outline-none"
            >
              {drilldown?.departments?.map(d => (
                <option key={d.department} value={d.department}>{d.department}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Level 3: Department Topics */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              Level 3: Top Research Topics in {selectedDept}
            </h4>
            <div className="space-y-1.5">
              {drilldown?.topics?.map((top, idx) => (
                <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-amber-50/40 border border-amber-100 text-xs">
                  <span className="font-semibold text-slate-800">{top.topic_name}</span>
                  <span className="text-amber-800 font-bold bg-amber-100 px-2 py-0.5 rounded text-[10px]">
                    {top.frequency} Searches
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Level 4: Active Researchers in Department */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              Level 4: Active Faculty & Researchers
            </h4>
            <div className="space-y-1.5">
              {drilldown?.members?.map(m => (
                <div key={m.user_id} className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs flex items-center justify-between">
                  <div>
                    <span className="font-bold text-slate-900">{m.full_name}</span>
                    <span className="text-[10px] text-slate-500 ml-1.5 capitalize">({m.role})</span>
                  </div>
                  <span className="text-[10px] text-slate-500 max-w-[150px] truncate">{m.interest_tags}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* TOP ENGAGED PAPERS LEADERBOARD */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <Award className="w-5 h-5 text-amber-500" />
            <h3 className="text-sm font-bold text-slate-900">Most Engaged Research Papers (Chanakya Hall of Fame)</h3>
          </div>
          <span className="text-xs text-slate-500">Scored via saves, discussion mentions, and citations</span>
        </div>

        <div className="space-y-2.5">
          {topPapers.map((p, idx) => (
            <div key={p.paper_id} className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between gap-4 text-xs">
              <div className="flex items-center gap-3">
                <span className="w-6 h-6 rounded-full bg-slate-900 text-amber-400 font-bold text-xs flex items-center justify-center shrink-0">
                  {idx + 1}
                </span>
                <div>
                  <h4 className="font-bold text-slate-900 leading-snug">{p.title}</h4>
                  <p className="text-[10px] text-slate-500">{p.authors} ({p.year}) • {p.department}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <span className="px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-semibold text-[10px]">
                  {p.library_saves} Saves
                </span>
                <span className="px-2 py-0.5 bg-purple-100 text-purple-800 rounded font-semibold text-[10px]">
                  {p.discussion_mentions} Mentions
                </span>
                <span className="px-2.5 py-1 bg-slate-900 text-amber-400 font-bold rounded-lg text-xs font-mono">
                  {Math.round(p.engagement_score)} pts
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
