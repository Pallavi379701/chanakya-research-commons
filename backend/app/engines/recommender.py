from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder

from app.models.models import User, Paper, LibraryItem, Follow
from app.engines.graph import graph_engine

class RecommendationEngine:
    def __init__(self):
        self.association_rules_df = None
        self.rules_computed = False

    def build_association_rules(self, db: Session):
        """
        Mine 'Members who saved this also saved' association rules using FP-Growth.
        Transactions = sets of papers saved by each user.
        """
        # Fetch all library saves grouped by user
        items = db.query(LibraryItem.user_id, LibraryItem.paper_id).all()
        if not items:
            self.rules_computed = True
            return

        user_baskets: Dict[int, List[str]] = {}
        for u_id, p_id in items:
            if u_id not in user_baskets:
                user_baskets[u_id] = []
            user_baskets[u_id].append(str(p_id))

        transactions = [list(set(basket)) for basket in user_baskets.values() if len(basket) >= 2]
        if len(transactions) < 5:
            self.rules_computed = True
            return

        try:
            te = TransactionEncoder()
            te_ary = te.fit(transactions).transform(transactions)
            df = pd.DataFrame(te_ary, columns=te.columns_)
            
            # Run FP-Growth
            frequent_itemsets = fpgrowth(df, min_support=0.04, use_colnames=True)
            if not frequent_itemsets.empty:
                rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.2)
                self.association_rules_df = rules
            self.rules_computed = True
        except Exception as e:
            print(f"FP-Growth notice: {e}")
            self.rules_computed = True

    def get_also_saved(self, db: Session, paper_id: int, top_n: int = 5) -> List[Dict[str, Any]]:
        """Return 'Members who saved this also saved' for a given paper."""
        if not self.rules_computed:
            self.build_association_rules(db)

        target_str = str(paper_id)
        recommended_paper_ids = []

        if self.association_rules_df is not None and not self.association_rules_df.empty:
            matching = self.association_rules_df[
                self.association_rules_df["antecedents"].apply(lambda s: target_str in s)
            ]
            if not matching.empty:
                sorted_rules = matching.sort_values(by=["confidence", "lift"], ascending=False)
                for _, row in sorted_rules.iterrows():
                    for item in row["consequents"]:
                        if int(item) != paper_id and int(item) not in recommended_paper_ids:
                            recommended_paper_ids.append(int(item))

        # Fallback to co-occurrence if FP-Growth yields few results
        if len(recommended_paper_ids) < top_n:
            co_saves = db.query(LibraryItem.paper_id)\
                .filter(LibraryItem.user_id.in_(
                    db.query(LibraryItem.user_id).filter(LibraryItem.paper_id == paper_id)
                ))\
                .filter(LibraryItem.paper_id != paper_id)\
                .all()
            counts = {}
            for (p_id,) in co_saves:
                counts[p_id] = counts.get(p_id, 0) + 1
            sorted_co = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            for p_id, _ in sorted_co:
                if p_id not in recommended_paper_ids:
                    recommended_paper_ids.append(p_id)

        papers = db.query(Paper).filter(Paper.id.in_(recommended_paper_ids[:top_n])).all()
        return [{
            "id": p.id,
            "title": p.title,
            "authors": p.authors,
            "year": p.year,
            "venue": p.venue,
            "department": p.department,
            "topics": p.topics
        } for p in papers]

    def recommend_papers_for_user(self, db: Session, user_id: int, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Hybrid Paper Recommendations:
        - Content-based profile matching against paper abstract embeddings
        - Collaborative filtering (items saved by similar users)
        - Cold-start handling for new users with no history
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        user_saved_ids = {item.paper_id for item in db.query(LibraryItem.paper_id).filter(LibraryItem.user_id == user_id).all()}
        
        # Cold start handling: if user has no saved papers
        is_cold_start = len(user_saved_ids) == 0

        # All candidate papers
        candidate_papers = db.query(Paper).filter(Paper.is_duplicate_planted == False).all()
        if not candidate_papers:
            return []

        # Content-based scoring
        user_interest_text = f"{user.research_interests} {user.interest_tags} {user.department}"
        corpus = [f"{p.title} {p.abstract} {p.topics} {p.department}" for p in candidate_papers]
        
        vec = TfidfVectorizer(max_features=3000, stop_words="english")
        try:
            tfidf_mat = vec.fit_transform(corpus)
            user_vec = vec.transform([user_interest_text])
            content_sims = cosine_similarity(user_vec, tfidf_mat).flatten()
        except Exception:
            content_sims = np.zeros(len(candidate_papers))

        # Collaborative filtering signal (users in same department and shared saves)
        collaborative_scores = np.zeros(len(candidate_papers))
        if not is_cold_start:
            similar_users = db.query(LibraryItem.user_id)\
                .filter(LibraryItem.paper_id.in_(user_saved_ids))\
                .filter(LibraryItem.user_id != user_id)\
                .all()
            sim_user_ids = [u_id for (u_id,) in similar_users]
            if sim_user_ids:
                co_saved = db.query(LibraryItem.paper_id)\
                    .filter(LibraryItem.user_id.in_(sim_user_ids))\
                    .all()
                for (p_id,) in co_saved:
                    for idx, cp in enumerate(candidate_papers):
                        if cp.id == p_id:
                            collaborative_scores[idx] += 1.0

        # Combine scores
        max_collab = max(collaborative_scores.max(), 1.0)
        norm_collab = collaborative_scores / max_collab

        scored_list = []
        for idx, p in enumerate(candidate_papers):
            if p.id in user_saved_ids:
                continue
            
            c_score = float(content_sims[idx])
            cf_score = float(norm_collab[idx])
            pr = graph_engine.get_score(p.id) * 10.0
            dept_bonus = 0.2 if p.department == user.department else 0.0

            if is_cold_start:
                # Cold start: rely on department prior + content profile + high PageRank
                final_score = 0.60 * c_score + 0.25 * dept_bonus + 0.15 * pr
            else:
                final_score = 0.45 * c_score + 0.35 * cf_score + 0.10 * dept_bonus + 0.10 * pr

            scored_list.append({
                "id": p.id,
                "title": p.title,
                "authors": p.authors,
                "venue": p.venue,
                "year": p.year,
                "department": p.department,
                "topics": p.topics,
                "recommendation_score": round(final_score, 4),
                "is_cold_start_fallback": is_cold_start
            })

        scored_list.sort(key=lambda x: x["recommendation_score"], reverse=True)
        return scored_list[:top_n]

    def recommend_members_to_connect(self, db: Session, user_id: int, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Recommend researchers to connect with based on:
        - Shared research tags and interests
        - Co-saved papers
        - Department alignment
        """
        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            return []

        # Current follows
        followed_ids = {f.following_id for f in db.query(Follow.following_id).filter(Follow.follower_id == user_id).all()}
        all_users = db.query(User).filter(User.id != user_id, User.is_spam == False).all()

        current_tags = set(t.strip().lower() for t in current_user.interest_tags.split(",") if t.strip())
        current_saves = {item.paper_id for item in db.query(LibraryItem.paper_id).filter(LibraryItem.user_id == user_id).all()}

        candidate_scores = []
        for other in all_users:
            if other.id in followed_ids:
                continue

            other_tags = set(t.strip().lower() for t in other.interest_tags.split(",") if t.strip())
            shared_tags = current_tags.intersection(other_tags)

            other_saves = {item.paper_id for item in db.query(LibraryItem.paper_id).filter(LibraryItem.user_id == other.id).all()}
            shared_saves = current_saves.intersection(other_saves)

            score = len(shared_tags) * 0.4 + len(shared_saves) * 0.3
            if other.department == current_user.department:
                score += 0.2

            candidate_scores.append({
                "id": other.id,
                "username": other.username,
                "full_name": other.full_name,
                "role": other.role,
                "department": other.department,
                "research_interests": other.research_interests,
                "interest_tags": other.interest_tags,
                "shared_topics": list(shared_tags),
                "shared_saved_count": len(shared_saves),
                "match_score": round(score, 3)
            })

        candidate_scores.sort(key=lambda x: x["match_score"], reverse=True)
        return candidate_scores[:top_n]

recommender_engine = RecommendationEngine()
