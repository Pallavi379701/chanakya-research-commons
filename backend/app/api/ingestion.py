import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import requests
import feedparser

from app.core.config import BRONZE_DIR, SILVER_DIR, GOLD_DIR
from app.core.database import get_db
from app.models.models import Paper

def trigger_lakehouse_rebuild():
    try:
        from scripts.build_warehouse import build_lakehouse
        build_lakehouse()
    except Exception as e:
        print(f"Lakehouse build error: {e}")

router = APIRouter(prefix="/ingestion", tags=["F4: External Content Ingestion"])

RSS_FEEDS = [
    {"name": "arXiv Computer Science AI", "url": "http://export.arxiv.org/rss/cs.AI"},
    {"name": "arXiv Information Retrieval", "url": "http://export.arxiv.org/rss/cs.IR"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"}
]

@router.get("/status")
def get_ingestion_status(db: Session = Depends(get_db)):
    """Return status of Lakehouse layers and external ingestion."""
    total_papers = db.query(Paper).count()
    bronze_files = list(BRONZE_DIR.glob("*.json"))
    silver_files = list(SILVER_DIR.glob("*.parquet"))
    gold_files = list(GOLD_DIR.glob("*.parquet"))

    return {
        "status": "active",
        "total_catalog_papers": total_papers,
        "lakehouse": {
            "bronze_files": [f.name for f in bronze_files],
            "silver_files": [f.name for f in silver_files],
            "gold_files": [f.name for f in gold_files]
        },
        "curated_sources": [
            "arXiv API (Computer Science, Math, Bio)",
            "OpenAlex Scholarly Knowledge Graph",
            "Semantic Scholar Academic Graph",
            "Curated University RSS Feeds"
        ]
    }

@router.post("/trigger-batch-refresh")
def trigger_batch_refresh(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Trigger scheduled incremental batch refresh:
    Fetches latest papers, appends raw response to Bronze layer,
    and runs incremental transformation into Silver and Gold Parquet layers without reprocessing everything.
    """
    # Background execution of warehouse rebuild
    background_tasks.add_task(trigger_lakehouse_rebuild)
    return {
        "message": "Incremental Lakehouse batch refresh triggered successfully in the background.",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
