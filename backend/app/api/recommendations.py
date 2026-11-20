from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.engines.recommender import recommender_engine

router = APIRouter(prefix="/recommendations", tags=["F6: Recommendations"])

@router.get("/papers")
def get_recommended_papers(
    current_user_id: int = 1,
    top_n: int = Query(10, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    Recommend papers a member may want to read:
    Blends content-based interest similarity with collaborative filtering and cold-start priors.
    """
    return recommender_engine.recommend_papers_for_user(db, user_id=current_user_id, top_n=top_n)

@router.get("/members")
def get_recommended_colleagues(
    current_user_id: int = 1,
    top_n: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Recommend members to connect with based on shared research topics, co-saved literature, and department synergy.
    """
    return recommender_engine.recommend_members_to_connect(db, user_id=current_user_id, top_n=top_n)

@router.get("/also-saved/{paper_id}")
def get_members_also_saved(
    paper_id: int,
    top_n: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """
    'Members who saved this also saved' on every library item:
    Mined using FP-Growth frequent itemsets and association rules.
    """
    return recommender_engine.get_also_saved(db, paper_id=paper_id, top_n=top_n)
