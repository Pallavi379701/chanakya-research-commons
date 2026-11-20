from typing import List, Dict, Any, Optional
import duckdb
from pathlib import Path
from app.core.config import GOLD_DIR

class AnalyticsWarehouseEngine:
    def __init__(self):
        self.con = duckdb.connect()
        self._init_tables()

    def _init_tables(self):
        """Register Gold Parquet files into DuckDB for fast columnar OLAP execution."""
        gold_files = {
            "dim_departments": GOLD_DIR / "dim_departments.parquet",
            "dim_date": GOLD_DIR / "dim_date.parquet",
            "dim_users": GOLD_DIR / "dim_users.parquet",
            "dim_papers": GOLD_DIR / "dim_papers.parquet",
            "fact_activity": GOLD_DIR / "fact_activity.parquet",
            "fact_paper_saves": GOLD_DIR / "fact_paper_saves.parquet",
            "fact_citations": GOLD_DIR / "fact_citations.parquet",
            "fact_discussions": GOLD_DIR / "fact_discussions.parquet"
        }

        for table_name, path in gold_files.items():
            if path.exists():
                self.con.execute(f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM read_parquet('{path.as_posix()}')")

    def get_department_trends_over_time(self) -> List[Dict[str, Any]]:
        """Research activity and saves by department over months."""
        self._init_tables()
        query = """
            SELECT 
                d.month_name,
                d.month,
                a.department,
                COUNT(a.event_id) as total_events,
                SUM(CASE WHEN a.event_type = 'save' THEN 1 ELSE 0 END) as saves_count,
                SUM(CASE WHEN a.event_type = 'search' THEN 1 ELSE 0 END) as searches_count,
                SUM(CASE WHEN a.event_type = 'view' THEN 1 ELSE 0 END) as views_count
            FROM fact_activity a
            JOIN dim_date d ON a.date_key = d.date_key
            WHERE a.department IS NOT NULL AND a.department != ''
            GROUP BY d.month_name, d.month, a.department
            ORDER BY d.month, total_events DESC
        """
        try:
            df = self.con.execute(query).fetchdf()
            return df.to_dict(orient="records")
        except Exception as e:
            print(f"DuckDB error in department trends: {e}")
            return []

    def get_cross_department_collaboration_network(self) -> Dict[str, Any]:
        """
        Cross-department interaction and collaboration matrix.
        Calculates citation links and joint paper saves bridging departments.
        Returns graph nodes (departments) and weighted links.
        """
        self._init_tables()
        # Query citations across departments
        query_citations = """
            SELECT 
                p1.department as source_dept,
                p2.department as target_dept,
                COUNT(*) as citation_count
            FROM fact_citations c
            JOIN dim_papers p1 ON c.source_paper_id = p1.paper_id
            JOIN dim_papers p2 ON c.target_paper_id = p2.paper_id
            WHERE p1.department != p2.department
            GROUP BY p1.department, p2.department
        """
        try:
            cit_df = self.con.execute(query_citations).fetchdf()
        except Exception:
            cit_df = None

        departments_df = self.con.execute("SELECT department_name FROM dim_departments").fetchdf()
        nodes = [{"id": dept, "name": dept, "group": idx + 1} for idx, dept in enumerate(departments_df["department_name"])]
        
        links = []
        if cit_df is not None and not cit_df.empty:
            for _, row in cit_df.iterrows():
                links.append({
                    "source": row["source_dept"],
                    "target": row["target_dept"],
                    "weight": int(row["citation_count"]),
                    "type": "citation_flow"
                })

        return {"nodes": nodes, "links": links}

    def get_top_engaged_papers(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Most saved and most discussed papers across Chanakya University."""
        self._init_tables()
        query = f"""
            SELECT 
                p.paper_id,
                p.title,
                p.authors,
                p.department,
                p.year,
                p.citation_count as external_citations,
                COALESCE(s.save_count, 0) as library_saves,
                COALESCE(d.discussion_count, 0) as discussion_mentions,
                (p.citation_count * 0.2 + COALESCE(s.save_count, 0) * 3 + COALESCE(d.discussion_count, 0) * 2) as engagement_score
            FROM dim_papers p
            LEFT JOIN (
                SELECT paper_id, COUNT(*) as save_count 
                FROM fact_paper_saves 
                GROUP BY paper_id
            ) s ON p.paper_id = s.paper_id
            LEFT JOIN (
                SELECT attached_paper_id as paper_id, COUNT(*) as discussion_count 
                FROM fact_discussions 
                WHERE attached_paper_id IS NOT NULL 
                GROUP BY attached_paper_id
            ) d ON p.paper_id = d.paper_id
            WHERE p.is_duplicate_planted = FALSE
            ORDER BY engagement_score DESC
            LIMIT {top_n}
        """
        try:
            df = self.con.execute(query).fetchdf()
            return df.to_dict(orient="records")
        except Exception as e:
            print(f"DuckDB error in top engaged papers: {e}")
            return []

    def drilldown_hierarchy(self, department: Optional[str] = None, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        4-Level Hierarchical Drill-down:
        University -> Department -> Topic -> Member
        """
        self._init_tables()
        
        # Level 1: University Summary
        uni_summary = self.con.execute("""
            SELECT 
                (SELECT COUNT(*) FROM dim_users WHERE is_spam = FALSE) as total_researchers,
                (SELECT COUNT(*) FROM dim_papers WHERE is_duplicate_planted = FALSE) as total_papers,
                (SELECT COUNT(*) FROM fact_paper_saves) as total_library_saves,
                (SELECT COUNT(*) FROM fact_discussions WHERE is_spam = FALSE) as total_discussions,
                (SELECT COUNT(*) FROM fact_activity) as total_warehouse_events
        """).fetchdf().to_dict(orient="records")[0]

        # Level 2: Department Level
        dept_breakdown = self.con.execute("""
            SELECT 
                department,
                COUNT(DISTINCT user_id) as researchers_count,
                COUNT(event_id) as activity_count
            FROM fact_activity
            WHERE department IS NOT NULL AND department != ''
            GROUP BY department
            ORDER BY activity_count DESC
        """).fetchdf().to_dict(orient="records")

        # Level 3: Topics within selected Department
        topic_breakdown = []
        target_dept = department or (dept_breakdown[0]["department"] if dept_breakdown else "Computer Science")
        if target_dept:
            topic_breakdown = self.con.execute(f"""
                SELECT 
                    query as topic_name,
                    COUNT(*) as frequency
                FROM fact_activity
                WHERE department = '{target_dept}' AND event_type = 'search' AND query IS NOT NULL AND query != ''
                GROUP BY query
                ORDER BY frequency DESC
                LIMIT 8
            """).fetchdf().to_dict(orient="records")

        # Level 4: Members in department
        members = self.con.execute(f"""
            SELECT 
                user_id,
                full_name,
                role,
                interest_tags
            FROM dim_users
            WHERE department = '{target_dept}' AND is_spam = FALSE
            LIMIT 10
        """).fetchdf().to_dict(orient="records")

        return {
            "university_summary": uni_summary,
            "departments": dept_breakdown,
            "selected_department": target_dept,
            "topics": topic_breakdown,
            "members": members
        }

warehouse_engine = AnalyticsWarehouseEngine()
