from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.models import Paper, LibraryItem, User, EventLog
from app.schemas.schemas import LibraryItemCreate, LibraryItemOut, PaperOut, PaperCreate
from app.engines.graph import graph_engine

router = APIRouter(prefix="/library", tags=["F3: University & Personal Library"])

@router.get("/my-items", response_model=List[LibraryItemOut])
def get_user_library(
    current_user_id: int = 1,
    collection_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve saved items for the active user, optionally filtered by collection/folder."""
    q = db.query(LibraryItem).filter(LibraryItem.user_id == current_user_id)
    if collection_name:
        q = q.filter(LibraryItem.collection_name == collection_name)
    
    items = q.order_by(LibraryItem.created_at.desc()).all()
    
    # Enrich with save count
    enriched = []
    for item in items:
        save_count = db.query(LibraryItem).filter(LibraryItem.paper_id == item.paper_id).count()
        item_out = LibraryItemOut.model_validate(item)
        if item.paper:
            p_out = PaperOut.model_validate(item.paper)
            p_out.save_count = save_count
            p_out.pagerank_score = round(graph_engine.get_score(p_out.id) * 1000, 4)
            item_out.paper = p_out
        enriched.append(item_out)
    return enriched

@router.get("/collections")
def get_user_collections(current_user_id: int = 1, db: Session = Depends(get_db)):
    """Return distinct collection folders with paper counts for the active user."""
    res = db.query(
        LibraryItem.collection_name, func.count(LibraryItem.id).label("count")
    ).filter(LibraryItem.user_id == current_user_id).group_by(LibraryItem.collection_name).all()
    return [{"collection_name": name, "count": cnt} for name, cnt in res]

@router.get("/chanakya-catalog", response_model=List[PaperOut])
def get_chanakya_library_catalog(
    department: Optional[str] = None,
    sort_by: str = "saves",  # saves, citations, recent
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    University-wide Chanakya Library:
    Lists all papers saved by members, showing university-wide save counts and citation metrics.
    """
    # Subquery for papers saved at least once
    saved_sub = db.query(
        LibraryItem.paper_id, func.count(LibraryItem.id).label("save_count")
    ).group_by(LibraryItem.paper_id).subquery()

    q = db.query(Paper, saved_sub.c.save_count).join(saved_sub, Paper.id == saved_sub.c.paper_id)
    
    if department:
        q = q.filter(Paper.department == department)
        
    if sort_by == "saves":
        q = q.order_by(saved_sub.c.save_count.desc())
    elif sort_by == "citations":
        q = q.order_by(Paper.citation_count.desc())
    else:
        q = q.order_by(Paper.created_at.desc())

    records = q.limit(limit).all()

    output = []
    for paper, count in records:
        p_out = PaperOut.model_validate(paper)
        p_out.save_count = count
        p_out.pagerank_score = round(graph_engine.get_score(paper.id) * 1000, 4)
        output.append(p_out)
    return output

@router.post("/save")
def save_paper(item_in: LibraryItemCreate, current_user_id: int = 1, db: Session = Depends(get_db)):
    """Save paper to user's collection and university-wide library."""
    paper = db.query(Paper).filter(Paper.id == item_in.paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    existing = db.query(LibraryItem).filter(
        LibraryItem.user_id == current_user_id,
        LibraryItem.paper_id == item_in.paper_id
    ).first()

    if existing:
        # Update notes / collection
        existing.notes = item_in.notes or existing.notes
        existing.collection_name = item_in.collection_name or existing.collection_name
        db.commit()
        return {"action": "updated", "item_id": existing.id}

    new_item = LibraryItem(
        user_id=current_user_id,
        paper_id=item_in.paper_id,
        notes=item_in.notes or "",
        collection_name=item_in.collection_name or "General"
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    # Log save event
    user = db.query(User).filter(User.id == current_user_id).first()
    db.add(EventLog(
        user_id=current_user_id,
        event_type="save",
        target_id=item_in.paper_id,
        department=user.department if user else None,
        timestamp=datetime.now(timezone.utc)
    ))
    db.commit()

    total_saves = db.query(LibraryItem).filter(LibraryItem.paper_id == item_in.paper_id).count()

    return {
        "action": "saved",
        "item_id": new_item.id,
        "paper_id": item_in.paper_id,
        "total_saves": total_saves
    }

@router.post("/add-manual", response_model=PaperOut)
def add_manual_paper(paper_in: PaperCreate, current_user_id: int = 1, db: Session = Depends(get_db)):
    """Add paper directly via URL, DOI, or arXiv ID."""
    # Check if DOI or arXiv already exists
    if paper_in.doi:
        existing = db.query(Paper).filter(Paper.doi == paper_in.doi).first()
        if existing:
            return existing
    if paper_in.arxiv_id:
        existing = db.query(Paper).filter(Paper.arxiv_id == paper_in.arxiv_id).first()
        if existing:
            return existing

    new_paper = Paper(
        title=paper_in.title,
        abstract=paper_in.abstract or "",
        authors=paper_in.authors or "Anonymous",
        venue=paper_in.venue or "Manual Entry",
        year=paper_in.year or datetime.now().year,
        doi=paper_in.doi or "",
        arxiv_id=paper_in.arxiv_id or "",
        url=paper_in.url or "",
        source=paper_in.source or "Manual",
        department=paper_in.department or "Computer Science",
        topics=paper_in.topics or "General Research",
        citation_count=1
    )
    db.add(new_paper)
    db.commit()
    db.refresh(new_paper)

    # Auto-save to user library
    lib_item = LibraryItem(
        user_id=current_user_id,
        paper_id=new_paper.id,
        notes="Added via manual import",
        collection_name="Imported"
    )
    db.add(lib_item)
    db.commit()

    p_out = PaperOut.model_validate(new_paper)
    p_out.save_count = 1
    return p_out
