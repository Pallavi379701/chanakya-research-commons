from typing import Dict, List, Any
import networkx as nx
from sqlalchemy.orm import Session
from app.models.models import Paper, PaperCitation

class CitationGraphEngine:
    def __init__(self, damping: float = 0.85):
        self.damping = damping
        self.graph = nx.DiGraph()
        self.pagerank_scores: Dict[int, float] = {}

    def build_graph(self, db: Session):
        """Construct citation graph from database and compute PageRank."""
        self.graph.clear()
        
        # Add all paper nodes
        papers = db.query(Paper.id).all()
        for (p_id,) in papers:
            self.graph.add_node(p_id)

        # Add citation edges: source_paper cites target_paper
        citations = db.query(PaperCitation.source_paper_id, PaperCitation.target_paper_id).all()
        for src, tgt in citations:
            if src in self.graph and tgt in self.graph:
                self.graph.add_edge(src, tgt)

        if len(self.graph.nodes) > 0:
            # NetworkX PageRank
            try:
                self.pagerank_scores = nx.pagerank(self.graph, alpha=self.damping, max_iter=100)
            except Exception:
                # Fallback if convergence issues
                uniform = 1.0 / len(self.graph.nodes)
                self.pagerank_scores = {n: uniform for n in self.graph.nodes}
        else:
            self.pagerank_scores = {}

    def get_score(self, paper_id: int) -> float:
        """Return normalized PageRank score for paper."""
        return self.pagerank_scores.get(paper_id, 0.0)

    def get_top_papers(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Return top authority papers by PageRank score."""
        sorted_nodes = sorted(self.pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [{"paper_id": p_id, "score": score} for p_id, score in sorted_nodes]

graph_engine = CitationGraphEngine()
