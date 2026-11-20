import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import DATA_DIR, BRONZE_DIR, SILVER_DIR, GOLD_DIR, DEPARTMENTS
from app.core.database import SessionLocal
from app.models.models import User, Paper, PaperCitation, LibraryItem, Post, Comment, EventLog

def build_lakehouse():
    print("Starting Lakehouse ELT Pipeline (Bronze -> Silver -> Gold Star Schema)...")
    db = SessionLocal()

    # ==========================================
    # 1. SILVER LAYER: Ingestion & Cleansing
    # ==========================================
    print("Transforming Bronze raw payloads into Silver cleansed datasets...")
    
    # Query raw papers from DB and bronze payloads
    papers_db = db.query(Paper).all()
    papers_data = []
    for p in papers_db:
        papers_data.append({
            "paper_id": p.id,
            "title": p.title.strip(),
            "abstract": p.abstract.strip(),
            "authors": p.authors.strip(),
            "venue": p.venue.strip(),
            "year": p.year,
            "doi": p.doi,
            "arxiv_id": p.arxiv_id,
            "url": p.url,
            "source": p.source,
            "department": p.department,
            "topics": p.topics,
            "citation_count": p.citation_count,
            "is_duplicate_planted": p.is_duplicate_planted,
            "duplicate_of_id": p.duplicate_of_id,
            "created_at": p.created_at
        })
    df_papers_silver = pd.DataFrame(papers_data)
    df_papers_silver.to_parquet(SILVER_DIR / "papers_silver.parquet", index=False)
    print(f"Saved Silver Papers: {len(df_papers_silver)} rows")

    # Users
    users_db = db.query(User).all()
    users_data = []
    for u in users_db:
        users_data.append({
            "user_id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "department": u.department,
            "research_interests": u.research_interests,
            "interest_tags": u.interest_tags,
            "is_spam": u.is_spam,
            "created_at": u.created_at
        })
    df_users_silver = pd.DataFrame(users_data)
    df_users_silver.to_parquet(SILVER_DIR / "users_silver.parquet", index=False)
    print(f"Saved Silver Users: {len(df_users_silver)} rows")

    # Events
    events_db = db.query(EventLog).all()
    events_data = []
    for e in events_db:
        events_data.append({
            "event_id": e.id,
            "user_id": e.user_id,
            "event_type": e.event_type,
            "target_id": e.target_id,
            "query": e.query or "",
            "department": e.department or "",
            "timestamp": e.timestamp
        })
    df_events_silver = pd.DataFrame(events_data)
    df_events_silver.to_parquet(SILVER_DIR / "events_silver.parquet", index=False)
    print(f"Saved Silver Events: {len(df_events_silver)} rows")

    # ==========================================
    # 2. GOLD LAYER: Star Schema Dimensional Model
    # ==========================================
    print("Building Gold Star Schema (Dimensional Modeling via DuckDB)...")
    con = duckdb.connect()

    # Dim Departments
    departments_data = [
        {"department_id": idx + 1, "department_name": dept, "faculty_count": len([u for u in users_db if u.department == dept and u.role == 'faculty']), "student_count": len([u for u in users_db if u.department == dept and u.role == 'student'])}
        for idx, dept in enumerate(DEPARTMENTS)
    ]
    df_dim_departments = pd.DataFrame(departments_data)
    df_dim_departments.to_parquet(GOLD_DIR / "dim_departments.parquet", index=False)

    # Dim Date (Generating date dimension for timeline analytics)
    dates_list = pd.date_range(start="2026-01-01", end="2026-07-01", freq="D")
    df_dim_date = pd.DataFrame({
        "date_key": dates_list.strftime("%Y%m%d").astype(int),
        "full_date": dates_list,
        "year": dates_list.year,
        "quarter": dates_list.quarter,
        "month": dates_list.month,
        "month_name": dates_list.strftime("%B"),
        "week_of_year": dates_list.isocalendar().week.astype(int),
        "day_of_week": dates_list.dayofweek,
        "day_name": dates_list.strftime("%A"),
        "is_weekend": dates_list.dayofweek >= 5
    })
    df_dim_date.to_parquet(GOLD_DIR / "dim_date.parquet", index=False)

    # Dim Users
    df_dim_users = df_users_silver[["user_id", "username", "full_name", "role", "department", "interest_tags", "is_spam"]].copy()
    df_dim_users.to_parquet(GOLD_DIR / "dim_users.parquet", index=False)

    # Dim Papers
    df_dim_papers = df_papers_silver[["paper_id", "title", "authors", "venue", "year", "source", "department", "citation_count", "is_duplicate_planted"]].copy()
    df_dim_papers.to_parquet(GOLD_DIR / "dim_papers.parquet", index=False)

    # Fact Activity (Connecting events with dimensional surrogate keys)
    con.register("events", df_events_silver)
    con.register("dates", df_dim_date)
    fact_activity_df = con.execute("""
        SELECT 
            e.event_id,
            e.user_id,
            d.date_key,
            e.timestamp,
            e.event_type,
            e.target_id,
            e.query,
            e.department
        FROM events e
        LEFT JOIN dates d ON strftime(e.timestamp, '%Y-%m-%d') = strftime(d.full_date, '%Y-%m-%d')
    """).fetchdf()
    fact_activity_df.to_parquet(GOLD_DIR / "fact_activity.parquet", index=False)

    # Fact Paper Saves (Library Saves)
    lib_db = db.query(LibraryItem).all()
    lib_data = [{
        "save_id": item.id,
        "user_id": item.user_id,
        "paper_id": item.paper_id,
        "collection_name": item.collection_name,
        "saved_at": item.created_at,
        "date_key": int(item.created_at.strftime("%Y%m%d"))
    } for item in lib_db]
    df_fact_saves = pd.DataFrame(lib_data)
    df_fact_saves.to_parquet(GOLD_DIR / "fact_paper_saves.parquet", index=False)

    # Fact Citations
    cits_db = db.query(PaperCitation).all()
    cits_data = [{
        "citation_id": c.id,
        "source_paper_id": c.source_paper_id,
        "target_paper_id": c.target_paper_id
    } for c in cits_db]
    df_fact_citations = pd.DataFrame(cits_data)
    df_fact_citations.to_parquet(GOLD_DIR / "fact_citations.parquet", index=False)

    # Fact Discussions
    posts_db = db.query(Post).all()
    posts_data = [{
        "post_id": p.id,
        "user_id": p.user_id,
        "attached_paper_id": p.attached_paper_id,
        "upvotes": p.upvotes,
        "is_spam": p.is_spam,
        "created_at": p.created_at,
        "date_key": int(p.created_at.strftime("%Y%m%d"))
    } for p in posts_db]
    df_fact_discussions = pd.DataFrame(posts_data)
    df_fact_discussions.to_parquet(GOLD_DIR / "fact_discussions.parquet", index=False)

    print("SUCCESS: Lakehouse ELT complete!")
    print(f"- Silver files written to {SILVER_DIR}")
    print(f"- Gold Star Schema tables written to {GOLD_DIR}")
    print("  * dim_departments, dim_date, dim_users, dim_papers")
    print("  * fact_activity, fact_paper_saves, fact_citations, fact_discussions")
    db.close()

if __name__ == "__main__":
    build_lakehouse()
