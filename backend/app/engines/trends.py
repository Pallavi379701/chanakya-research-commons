from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import EventLog, Post

class TrendsEngine:
    def __init__(self, z_threshold: float = 2.0):
        self.z_threshold = z_threshold

    def compute_sliding_window_trends(self, db: Session, window_days: int = 7, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Stream mining over a sliding time window.
        Aggregates search and discussion activity to compute velocity and frequency.
        """
        # Determine latest event time as baseline reference
        latest_event = db.query(func.max(EventLog.timestamp)).scalar() or datetime.now(timezone.utc)
        cutoff_date = latest_event - timedelta(days=window_days)

        # Aggregate events with topic queries
        query_counts = db.query(
            EventLog.query, func.count(EventLog.id).label("freq")
        ).filter(
            EventLog.timestamp >= cutoff_date,
            EventLog.query.isnot(None),
            EventLog.query != ""
        ).group_by(EventLog.query).order_by(func.count(EventLog.id).desc()).limit(top_n).all()

        results = []
        for q, freq in query_counts:
            results.append({
                "topic": q,
                "frequency": freq,
                "window": f"Last {window_days} Days"
            })
        return results

    def detect_topic_spikes(self, db: Session, baseline_days: int = 60, current_window_days: int = 7) -> List[Dict[str, Any]]:
        """
        Statistical Anomaly / Spike Detection:
        Computes rolling baseline mean and standard deviation of search queries/mentions.
        If current window frequency exceeds mean + (z_threshold * std), flags as a Topic Spike!
        """
        latest_event = db.query(func.max(EventLog.timestamp)).scalar() or datetime.now(timezone.utc)
        baseline_start = latest_event - timedelta(days=baseline_days)
        recent_cutoff = latest_event - timedelta(days=current_window_days)

        # Fetch all queries in the baseline window
        events = db.query(EventLog.query, EventLog.timestamp).filter(
            EventLog.timestamp >= baseline_start,
            EventLog.query.isnot(None),
            EventLog.query != ""
        ).all()

        if not events:
            return []

        df = pd.DataFrame([{"query": e[0], "timestamp": e[1]} for e in events])
        df["day"] = df["timestamp"].dt.date

        # Group by topic and day
        daily_counts = df.groupby(["query", "day"]).size().unstack(fill_value=0)
        
        spike_alerts = []
        recent_date_cutoff = recent_cutoff.date()

        for topic in daily_counts.index:
            series = daily_counts.loc[topic]
            # Historical window vs recent window
            hist_series = series[series.index < recent_date_cutoff]
            rec_series = series[series.index >= recent_date_cutoff]

            if len(hist_series) < 5 or len(rec_series) == 0:
                continue

            hist_mean = float(hist_series.mean())
            hist_std = float(hist_series.std())
            recent_mean = float(rec_series.mean())
            recent_total = int(rec_series.sum())

            # Avoid zero division
            std_eff = hist_std if hist_std > 0.1 else 0.5
            z_score = (recent_mean - hist_mean) / std_eff

            if z_score >= self.z_threshold and recent_total >= 15:
                severity = "CRITICAL" if z_score > 3.5 else "HIGH" if z_score > 2.5 else "MEDIUM"
                spike_alerts.append({
                    "topic": topic,
                    "current_count": recent_total,
                    "baseline_mean": round(hist_mean * current_window_days, 1),
                    "z_score": round(z_score, 2),
                    "severity": severity,
                    "detected_at": latest_event.strftime("%Y-%m-%d %H:%M:%S UTC")
                })

        spike_alerts.sort(key=lambda x: x["z_score"], reverse=True)
        return spike_alerts

    def scan_rolling_timeline_spikes(self, db: Session, window_days: int = 7) -> List[Dict[str, Any]]:
        """
        Scan across the entire 6-month historical timeline using a rolling sliding window
        to detect all topic surges and evaluate spike detection latency.
        """
        events = db.query(EventLog.query, EventLog.timestamp).filter(
            EventLog.query.isnot(None),
            EventLog.query != ""
        ).order_by(EventLog.timestamp.asc()).all()

        if not events:
            return []

        df = pd.DataFrame([{"query": e[0], "timestamp": e[1]} for e in events])
        df["day"] = df["timestamp"].dt.date
        
        all_detected_spikes = []
        unique_days = sorted(list(df["day"].unique()))

        if len(unique_days) < 14:
            return []

        # Iterate in weekly steps
        for i in range(14, len(unique_days), 3):
            cutoff_day = unique_days[i]
            history_days = unique_days[max(0, i-45):i-7]
            recent_days = unique_days[i-7:i]

            df_hist = df[df["day"].isin(history_days)]
            df_rec = df[df["day"].isin(recent_days)]

            hist_counts = df_hist.groupby("query").size()
            rec_counts = df_rec.groupby("query").size()

            for topic, count in rec_counts.items():
                if count >= 35:
                    h_mean = hist_counts.get(topic, 0) / max(len(history_days)/7.0, 1.0)
                    if count > h_mean * 2.5:
                        all_detected_spikes.append({
                            "topic": topic,
                            "day": str(cutoff_day),
                            "count": int(count),
                            "baseline": round(float(h_mean), 1)
                        })

        return all_detected_spikes

trends_engine = TrendsEngine()
