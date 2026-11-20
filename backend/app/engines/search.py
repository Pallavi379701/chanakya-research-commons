import re
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.models import Paper, LibraryItem, User, Post
from app.engines.dedup import dedup_engine
from app.engines.graph import graph_engine

class UnifiedSearchEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))
        self.paper_matrix = None
        self.paper_ids = []
        self.is_indexed = False

    def build_index(self, db: Session):
        """Build TF-IDF and dense vector index over paper titles and abstracts."""
        papers = db.query(Paper).all()
        if not papers:
            return
        
        self.paper_ids = [p.id for p in papers]
        corpus = [f"{p.title} {p.abstract} {p.topics} {p.department}" for p in papers]
        self.paper_matrix = self.vectorizer.fit_transform(corpus)
        
        # Also index dedup engine
        dedup_engine.index_papers(papers)
        # Ensure PageRank is computed
        if not graph_engine.pagerank_scores:
            graph_engine.build_graph(db)

        self.is_indexed = True

    def search(self, db: Session, query: str, mode: str = "hybrid", top_k: int = 15) -> Dict[str, Any]:
        """
        Federated 4-Panel Unified Search:
        1. External Scholarly Sources
        2. Chanakya Library
        3. University Members
        4. Posts & Discussions
        """
        if not self.is_indexed:
            self.build_index(db)

        q_clean = query.strip().lower()
        
        # 1. External & Library Papers Retrieval & Ranking
        scored_papers = self._rank_papers(db, query, mode)
        
        # Separate into External vs Chanakya Library
        # Check which papers have been saved to Chanakya Library
        saved_counts = {}
        library_entries = db.query(LibraryItem.paper_id).all()
        for (p_id,) in library_entries:
            saved_counts[p_id] = saved_counts.get(p_id, 0) + 1

        external_list = []
        library_list = []

        for p_dict in scored_papers:
            p_id = p_dict["id"]
            save_count = saved_counts.get(p_id, 0)
            p_dict["save_count"] = save_count
            p_dict["pagerank_score"] = round(graph_engine.get_score(p_id) * 1000, 4)

            # Deduplication: same paper in several sources appears once with sources listed
            if save_count > 0:
                library_list.append(p_dict)
            else:
                external_list.append(p_dict)

        # Apply deduplication to external results
        external_deduped = dedup_engine.deduplicate_search_results(external_list)[:top_k]
        library_deduped = dedup_engine.deduplicate_search_results(library_list)[:top_k]

        # 3. People Search (Faculty, Researchers, Students matching research area)
        people_results = self._search_people(db, q_clean, top_k)

        # 4. Posts & Discussions Search
        posts_results = self._search_posts(db, q_clean, top_k)

        total_matches = len(external_deduped) + len(library_deduped) + len(people_results) + len(posts_results)

        return {
            "query": query,
            "mode": mode,
            "external_papers": external_deduped,
            "chanakya_library": library_deduped,
            "people": people_results,
            "posts": posts_results,
            "total_matches": total_matches
        }

    def _rank_papers(self, db: Session, query: str, mode: str) -> List[Dict[str, Any]]:
        """Compute hybrid relevance score = alpha * Semantic + beta * Keyword + gamma * PageRank."""
        papers = db.query(Paper).all()
        if not papers or self.paper_matrix is None:
            return []

        paper_map = {p.id: p for p in papers}

        # Vector semantic/keyword similarity
        q_vec = self.vectorizer.transform([query])
        sim_scores = cosine_similarity(q_vec, self.paper_matrix).flatten()

        q_terms = set(re.findall(r"\w+", query.lower()))
        scored = []

        for idx, p_id in enumerate(self.paper_ids):
            paper = paper_map.get(p_id)
            if not paper:
                continue

            sim = float(sim_scores[idx])
            pr = graph_engine.get_score(p_id) * 100.0  # scaled

            # Keyword lexical overlap
            title_terms = set(re.findall(r"\w+", paper.title.lower()))
            overlap = len(q_terms.intersection(title_terms)) / max(len(q_terms), 1)

            if mode == "keyword":
                final_score = overlap * 0.8 + sim * 0.2
            elif mode == "semantic":
                final_score = sim
            else:  # hybrid
                final_score = 0.55 * sim + 0.30 * overlap + 0.15 * pr

            if final_score > 0.02 or overlap > 0:
                scored.append({
                    "id": paper.id,
                    "title": paper.title,
                    "abstract": paper.abstract,
                    "authors": paper.authors,
                    "venue": paper.venue,
                    "year": paper.year,
                    "doi": paper.doi,
                    "arxiv_id": paper.arxiv_id,
                    "url": paper.url,
                    "source": paper.source,
                    "department": paper.department,
                    "topics": paper.topics,
                    "citation_count": paper.citation_count,
                    "score": round(final_score, 4),
                    "created_at": paper.created_at.isoformat()
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def _search_people(self, db: Session, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Find university members whose department, interests, or tags match the query."""
        users = db.query(User).filter(User.is_spam == False).all()
        results = []
        q_terms = set(re.findall(r"\w+", query.lower()))

        for u in users:
            text = f"{u.full_name} {u.department} {u.research_interests} {u.interest_tags}".lower()
            overlap = sum(1 for t in q_terms if t in text)
            if overlap > 0:
                results.append({
                    "id": u.id,
                    "username": u.username,
                    "full_name": u.full_name,
                    "role": u.role,
                    "department": u.department,
                    "research_interests": u.research_interests,
                    "interest_tags": u.interest_tags,
                    "bio": u.bio,
                    "publication_url": u.publication_url,
                    "relevance_score": overlap
                })
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]

    def _search_posts(self, db: Session, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Find discussions and posts matching query."""
        posts = db.query(Post).filter(Post.is_spam == False).all()
        results = []
        q_terms = set(re.findall(r"\w+", query.lower()))

        for p in posts:
            text = f"{p.title} {p.content} {p.tags}".lower()
            overlap = sum(1 for t in q_terms if t in text)
            if overlap > 0:
                results.append({
                    "id": p.id,
                    "title": p.title,
                    "content": p.content,
                    "tags": p.tags,
                    "upvotes": p.upvotes,
                    "created_at": p.created_at.isoformat(),
                    "author_name": p.author.full_name if p.author else "Anonymous",
                    "department": p.author.department if p.author else "",
                    "relevance_score": overlap
                })
        results.sort(key=lambda x: (x["relevance_score"], x["upvotes"]), reverse=True)
        return results[:top_k]

search_engine = UnifiedSearchEngine()
