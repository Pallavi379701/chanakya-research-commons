import React, { useState, useEffect } from 'react';
import { TrendingUp, AlertTriangle, ShieldAlert, Sparkles, Clock, Activity, AlertOctagon } from 'lucide-react';
import { api } from '../services/api';

export function TrendsPage({ currentUser }) {
  const [trends, setTrends] = useState(null);
  const [spamFlags, setSpamFlags] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadTrends = async () => {
    setLoading(true);
    try {
      const [trendData, spamData] = await Promise.all([
        api.getTrendsSummary(),
        api.getSpamFlags()
      ]);
      setTrends(trendData);
      setSpamFlags(spamData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTrends();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-amber-500" /> Trends & Stream Anomaly Monitoring
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time sliding window frequency analysis, statistical Z-score topic spike alerts, and automated academic spam detection.
          </p>
        </div>
        <button
          onClick={loadTrends}
          className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg"
        >
          Refresh Stream
        </button>
      </div>

      {/* ACTIVE TOPIC SPIKE ALERTS BANNER */}
      {trends?.active_spikes && trends.active_spikes.length > 0 && (
        <div className="bg-amber-500/10 border-2 border-amber-500/40 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-amber-900 font-bold text-sm">
            <AlertTriangle className="w-5 h-5 text-amber-600 animate-pulse" />
            <span>Active Topic Spike Alerts ({trends.active_spikes.length} Surges Detected)</span>
          </div>
          <p className="text-xs text-amber-950">
            Statistical anomaly detected: The following research topics have surged beyond normal variance (Z-score ≥ 2.0) over recent sliding windows:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
            {trends.active_spikes.map((spike, i) => (
              <div key={i} className="bg-white p-4 rounded-xl border border-amber-200 shadow-sm space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900 text-xs">{spike.topic}</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    spike.severity === 'CRITICAL' ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'
                  }`}>
                    {spike.severity}
                  </span>
                </div>
                <div className="text-[11px] text-slate-600">
                  Current Count: <strong className="text-slate-900">{spike.current_count} mentions</strong>
                </div>
                <div className="text-[10px] text-slate-500">
                  Baseline Expected: {spike.baseline_mean} • Z-Score: <strong className="text-amber-700 font-mono">+{spike.z_score}σ</strong>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 7-DAY & 30-DAY SLIDING WINDOWS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 7-Day Window */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-indigo-600" />
              <h3 className="text-sm font-bold text-slate-900">7-Day Fast Sliding Window</h3>
            </div>
            <span className="text-[10px] bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full font-semibold">
              Recent Velocity
            </span>
          </div>

          <div className="space-y-2.5">
            {trends?.trending_topics_7d.map((t, idx) => (
              <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 text-[10px] font-bold flex items-center justify-center">
                    {idx + 1}
                  </span>
                  <span className="font-semibold text-slate-800">{t.topic}</span>
                </div>
                <span className="font-bold text-indigo-700 bg-indigo-100/60 px-2 py-0.5 rounded text-[11px]">
                  {t.frequency} events
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* 30-Day Window */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-600" />
              <h3 className="text-sm font-bold text-slate-900">30-Day Macro Research Window</h3>
            </div>
            <span className="text-[10px] bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full font-semibold">
              Monthly Cumulative
            </span>
          </div>

          <div className="space-y-2.5">
            {trends?.trending_topics_30d.map((t, idx) => (
              <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 text-[10px] font-bold flex items-center justify-center">
                    {idx + 1}
                  </span>
                  <span className="font-semibold text-slate-800">{t.topic}</span>
                </div>
                <span className="font-bold text-emerald-700 bg-emerald-100/60 px-2 py-0.5 rounded text-[11px]">
                  {t.frequency} events
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ADMIN SPAM MODERATION QUEUE */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-600" />
            <div>
              <h3 className="text-sm font-bold text-slate-900">Admin Academic Integrity & Spam Queue</h3>
              <p className="text-xs text-slate-500">Heuristic pattern scanner flags bot bursts, essay mill promotions & unverified links</p>
            </div>
          </div>
          <span className="text-xs font-bold px-3 py-1 bg-rose-100 text-rose-800 rounded-full">
            {spamFlags?.total_flags || 0} Flagged Items
          </span>
        </div>

        {spamFlags?.flagged_posts && (
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Flagged Posts for Review</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {spamFlags.flagged_posts.slice(0, 6).map((item, idx) => (
                <div key={idx} className="p-3.5 bg-rose-50/30 border border-rose-200 rounded-xl text-xs space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900 text-[11px] truncate">{item.title}</span>
                    <span className="text-[10px] bg-rose-100 text-rose-800 font-bold px-2 py-0.5 rounded">
                      {Math.round(item.confidence * 100)}% Confidence
                    </span>
                  </div>
                  <p className="text-slate-600 text-[11px] italic">"{item.content}"</p>
                  <div className="text-[10px] text-rose-700 font-medium">
                    Reason: {item.reason}
                  </div>
                  <div className="text-[10px] text-slate-400">
                    Author: {item.author_name} (@{item.author_username}) • {item.created_at}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
