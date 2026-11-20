from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.schemas import AssistantQuery, AssistantResponse
from app.engines.rag_engine import rag_engine

router = APIRouter(prefix="/assistant", tags=["F8: Research Assistant"])

@router.post("/ask", response_model=AssistantResponse)
def ask_research_assistant(query_in: AssistantQuery, db: Session = Depends(get_db)):
    """
    RAG Research Assistant:
    Accepts a natural language question, retrieves grounded paper passages,
    and returns a synthesized response with bracketed citations [1] and verifiable source excerpts.
    """
    res = rag_engine.answer_query(db, question=query_in.question, top_k=query_in.top_k or 4)
    return res
