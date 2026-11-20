from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import SessionLocal
from app.engines.search import search_engine
from app.engines.graph import graph_engine
from app.engines.recommender import recommender_engine
from app.engines.rag_engine import rag_engine

from app.api.auth import router as auth_router
from app.api.posts import router as posts_router
from app.api.library import router as library_router
from app.api.ingestion import router as ingestion_router
from app.api.search import router as search_router
from app.api.recommendations import router as recommendations_router
from app.api.trends import router as trends_router
from app.api.assistant import router as assistant_router
from app.api.analytics import router as analytics_router
from app.api.evaluation import router as evaluation_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up indexing and graph on startup
    print("Initializing Chanakya Research Commons engines on startup...")
    db = SessionLocal()
    try:
        graph_engine.build_graph(db)
        search_engine.build_index(db)
        recommender_engine.build_association_rules(db)
        rag_engine.build_knowledge_base(db)
        print("Engines warmed up successfully!")
    except Exception as e:
        print(f"Engine warmup notice: {e}")
    finally:
        db.close()
    yield

app = FastAPI(
    title="Chanakya Research Commons API",
    description="Full-stack Data Mining and Warehousing research discovery and analytics platform for Chanakya University.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Subsystems F1 - F9 & Evaluation
app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(library_router)
app.include_router(ingestion_router)
app.include_router(search_router)
app.include_router(recommendations_router)
app.include_router(trends_router)
app.include_router(assistant_router)
app.include_router(analytics_router)
app.include_router(evaluation_router)

@app.get("/")
def root():
    return {
        "platform": "Chanakya Research Commons",
        "university": "Chanakya University, Bangalore",
        "course": "Data Mining and Warehousing (V Semester, B.Tech. 2026-27)",
        "subsystems": {
            "F1": "Accounts & Profiles (/auth)",
            "F2": "Posts & Discussions (/posts)",
            "F3": "Library & Collections (/library)",
            "F4": "External Ingestion & Lakehouse (/ingestion)",
            "F5": "Unified 4-Panel Search (/search)",
            "F6": "Recommendations (/recommendations)",
            "F7": "Trends & Anomaly Monitoring (/trends)",
            "F8": "Research Assistant RAG (/assistant)",
            "F9": "Institutional Analytics Star Schema (/analytics)",
            "Evaluation": "Quantitative Benchmarks against Ground Truth (/evaluation)"
        },
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
