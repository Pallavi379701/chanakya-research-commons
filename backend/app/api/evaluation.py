from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.schemas import BenchmarkReport
from app.engines.evaluation import benchmark_engine

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Benchmarks"])

@router.get("/run", response_model=BenchmarkReport)
def run_evaluation_benchmarks(db: Session = Depends(get_db)):
    """
    Executes live quantitative evaluation against planted ground truth:
    - MinHash LSH vs Exact Match Deduplication (Precision, Recall, F1)
    - Spam Detection (Precision, Recall, F1)
    - Topic Spike Detection (Recall, Latency)
    - Search & Recommendation Ranking (NDCG@10, MRR)
    - RAG Grounding Faithfulness Ratio
    """
    return benchmark_engine.evaluate_all(db)
