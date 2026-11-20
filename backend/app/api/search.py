from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import EventLog, User
from app.schemas.schemas import SearchResponse
from app.engines.search import search_engine

router = APIRouter(prefix="/search", tags=["F5: Unified Search"])

@router.get("", response_model=SearchResponse)
def execute_unified_search(
    q: str = Query(..., min_length=1, description="Search keywords or semantic research question"),
    mode: str = Query("hybrid", regex="^(keyword|semantic|hybrid)$"),
    top_k: int = Query(12, ge=1, le=50),
    current_user_id: Optional[int] = 1,
    db: Session = Depends(get_db)
):
    """
    Centerpiece: Unified 4-Panel Search
    Returns 4 simultaneous panels:
    1. External Scholarly Sources (with deduplicated sources)
    2. Chanakya Library (with member save counts)
    3. University Members & Researchers
    4. Posts & Discussions
    """
    # Execute search
    results = search_engine.search(db, query=q, mode=mode, top_k=top_k)

    # Log search event for trend mining and analytics
    user = db.query(User).filter(User.id == current_user_id).first() if current_user_id else None
    db.add(EventLog(
        user_id=current_user_id,
        event_type="search",
        query=q,
        department=user.department if user else None,
        timestamp=datetime.now(timezone.utc)
    ))
    db.commit()

    return results
