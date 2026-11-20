from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.engines.trends import trends_engine
from app.engines.spam_detector import spam_engine
from app.schemas.schemas import TrendsResponse

router = APIRouter(prefix="/trends", tags=["F7: Trends & Anomaly Monitoring"])

@router.get("/summary", response_model=TrendsResponse)
def get_trends_summary(db: Session = Depends(get_db)):
    """
    Returns sliding window topic trends, statistical spike alerts,
    and count of spam activity flags.
    """
    trends_7d = trends_engine.compute_sliding_window_trends(db, window_days=7, top_n=8)
    trends_30d = trends_engine.compute_sliding_window_trends(db, window_days=30, top_n=8)
    spikes = trends_engine.detect_topic_spikes(db)
    flagged_posts = spam_engine.scan_all_posts(db)

    return TrendsResponse(
        trending_topics_7d=trends_7d,
        trending_topics_30d=trends_30d,
        active_spikes=spikes,
        spam_flags_count=len(flagged_posts)
    )

@router.get("/spam-flags")
def get_admin_spam_flags(db: Session = Depends(get_db)):
    """Admin endpoint: lists flagged spam posts and abnormal accounts for moderation."""
    posts = spam_engine.scan_all_posts(db)
    accounts = spam_engine.scan_spam_accounts(db)
    return {
        "flagged_posts": posts,
        "flagged_accounts": accounts,
        "total_flags": len(posts) + len(accounts)
    }
