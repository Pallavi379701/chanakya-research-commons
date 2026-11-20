from typing import Optional
from fastapi import APIRouter, Query

from app.engines.warehouse import warehouse_engine

router = APIRouter(prefix="/analytics", tags=["F9: Institutional Analytics Dashboard"])

@router.get("/department-trends")
def get_department_trends():
    """Returns research activity by department over time (months)."""
    return warehouse_engine.get_department_trends_over_time()

@router.get("/collaboration-network")
def get_collaboration_network():
    """Returns cross-department collaboration network (nodes & edges) for interactive graph visualization."""
    return warehouse_engine.get_cross_department_collaboration_network()

@router.get("/top-engaged-papers")
def get_top_papers(limit: int = Query(10, ge=1, le=50)):
    """Returns most saved and discussed papers across the university."""
    return warehouse_engine.get_top_engaged_papers(top_n=limit)

@router.get("/drilldown")
def get_hierarchical_drilldown(
    department: Optional[str] = Query(None, description="Department to drill down into"),
    topic: Optional[str] = Query(None, description="Topic to drill down into")
):
    """
    4-Level Hierarchical Drill-down:
    University -> Department -> Topic -> Member
    """
    return warehouse_engine.drilldown_hierarchy(department=department, topic=topic)
