# Chanakya Research Commons (CRC)
> **A Unified Research Intelligence, Discovery & Data Warehousing Platform for Chanakya University**  
> *Course: Data Mining and Warehousing (V Semester, B.Tech. 2026–27)*  
> *School of Engineering, Chanakya University, Bangalore*

---

## 📌 Project Overview
Chanakya Research Commons (CRC) is a full-stack web platform and data lakehouse system designed to eliminate academic silos across university departments. 

For any research query, the platform presents a unified 4-panel federated view:
1. **External Scholarly Sources** (arXiv, OpenAlex, Semantic Scholar, curated research RSS feeds)
2. **Chanakya University Library** (internally saved literature with aggregated campus save counts)
3. **University Colleagues & Faculty** active in that domain
4. **Campus Discussions & Seminars** on the platform

Behind the web interface, CRC features a Medallion Data Lakehouse (Bronze raw lake, Silver cleansed tables, and Gold Star Schema Parquet files) queried via columnar DuckDB, and intelligent data mining algorithms evaluated with exact numbers against planted ground truth.

---

## 🚀 Key Functional Subsystems (F1–F9)

| Subsystem | Name | Implementation & Course Concepts |
| :--- | :--- | :--- |
| **F1** | **Accounts & Profiles** | Role-based authentication (Student, Faculty, Researcher, Admin), departments, research interests, publication URLs, member/topic follow graphs. |
| **F2** | **Posts & Discussions** | Threaded discussion forums, tags, paper attachments, upvoting, nested comments, and a personalized feed blending followed colleagues, topics, and trending debates. |
| **F3** | **University & Personal Library** | Save papers from search or direct URL / DOI / arXiv import, organize into personal collections with private research notes, global campus save counters. |
| **F4** | **External Content Ingestion** | Ingestion pipeline fetching metadata/abstracts from arXiv/OpenAlex and RSS feeds; raw responses stored unchanged in Bronze lake, transformed incrementally into Silver and Gold layers. |
| **F5** | **Unified Search (Centrepiece)** | Single search interface returning 4 simultaneous panels (External, Library, People, Posts). Dual keyword (BM25) and dense semantic vector search with NetworkX citation graph PageRank scoring and MinHash LSH deduplication. |
| **F6** | **Recommendations Hub** | "Papers you may want to read" (content profile cosine similarity + collaborative filtering), "Researchers to connect with", and FP-Growth association rules ("Members who saved this also saved") with cold-start priors. |
| **F7** | **Trends & Anomaly Monitoring** | Stream mining over 7-day and 30-day sliding windows, statistical Z-score anomaly detector flagging surging topics (Z ≥ 2.0), and automated heuristic regex/link spam moderation queue. |
| **F8** | **Grounded Research Assistant** | Natural language Q&A engine grounded in retrieved literature passages with bracketed citations (`[1]`, `[2]`), accompanied by verifiable source excerpts to eliminate hallucinations. |
| **F9** | **Institutional Analytics Dashboard** | Admin star schema analytics powered by columnar DuckDB over Parquet files, featuring cross-department collaboration network graphs, department trends over time, and a 4-level drilldown (University ➔ Department ➔ Topic ➔ Member). |

---

## 📊 Planted Ground Truth & Quantitative Evaluation Suite

In compliance with the project assessment criteria (where intelligent features carry half the marks and must be evaluated with numbers):
- **Seed Corpus**: 600 scholarly papers with abstracts and 2,431 citation edges across 6 departments (Computer Science, Data Science & AI, Electrical Engineering, Biotechnology, Mathematics & Computing, and Management).
- **Synthetic Activity**: 65 members, 2,360 posts and comments, and 11,700 interaction events spread across 180 days with weekday/weekend seasonal rhythms.
- **Planted Ground Truth (`backend/data/ground_truth_planted.json`)**:
  - 30 near-duplicate paper pairs (preprints, title perturbations, author name variants).
  - 10 spam accounts and 60 promotional spam posts.
  - 3 anomalous topic spikes injected at distinct historical weeks.

### Benchmark Results Summary
```
=========================================================================================================
Feature Area                        | Evaluated Method       | Metric       | Score    | Baseline
=========================================================================================================
F5: Near-Duplicate Resolution       | MinHash + LSH (Jaccard)| F1 Score     | 1.000    | 0.462
F5: Near-Duplicate Precision        | MinHash + LSH          | Precision    | 1.000    | 1.000
F7: Spam Detection (Posts)          | Heuristic Classifier   | F1 Score     | 1.000    | 0.380
F7: Spam Detection Precision        | Heuristic Classifier   | Precision    | 1.000    | 0.420
F7: Topic Spike Anomaly Detection   | Sliding Window Z-Score | Detection Rate| 1.000   | 0.330
F5: Search Ranking Quality          | Hybrid (Semantic+PR)   | NDCG@10      | 0.884    | 0.692
F6: Recommendation Relevance        | Hybrid + FP-Growth     | MRR          | 0.825    | 0.280
F8: RAG Research Assistant Grounding| Vector Cosine Retrieva | Faithfulness | 0.960    | 0.580
=========================================================================================================
```

---

## 💻 Tech Stack & Architectural Layers

- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons.
- **Backend API**: FastAPI (Python 3.11+), Uvicorn, Pydantic v2.
- **OLTP Database (Transactional)**: SQLite + SQLAlchemy (zero-config, portable).
- **OLAP Warehouse (Analytical)**: Columnar DuckDB running over partitioned Parquet files (Medallion architecture).
- **Data Mining & Graph Libraries**: NetworkX (PageRank), datasketch (MinHash/LSH), mlxtend (FP-Growth), scikit-learn (TF-IDF/cosine similarity).

---

## 🛠️ Quickstart & Local Setup Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### Method 1: Single-Click Launch (Windows)
Double-click `run_app.bat` in the repository root. This starts both the FastAPI backend (`http://127.0.0.1:8000`) and the Vite React frontend (`http://localhost:5173`).

---

### Method 2: Manual Terminal Setup

#### 1. Setup Backend
```powershell
cd backend
python -m pip install -r requirements.txt

# Generate synthetic dataset and planted ground truth (if not already seeded)
python scripts/generate_synthetic_data.py

# Build Bronze -> Silver -> Gold Star Schema Lakehouse
python scripts/build_warehouse.py

# Start Backend Server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2. Setup Frontend
```powershell
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 🧪 Running Automated Tests and Reproducing Benchmarks

### 1. Reproduce Quantitative Evaluation Metrics
Run the CLI evaluation benchmark suite:
```powershell
python backend/scripts/run_benchmarks.py
```
Or open the **Evaluation Lab** tab directly in the web UI and click **"Re-run Live Benchmarks"** to watch the metrics compute dynamically!

### 2. Run Automated API Test Suite
```powershell
python -m pytest backend/tests/test_api.py -v
```

---

## 🐳 Docker Deployment
To package and run with Docker Compose:
```bash
docker-compose up --build
```
- Web Application UI: `http://localhost:3000`
- Backend Swagger Docs: `http://localhost:8000/docs`

---

## 📄 Academic Deliverables
- **Technical Report**: Complete academic report mapping to the 40% demo/report rubric is located at [`report/TECHNICAL_REPORT.md`](report/TECHNICAL_REPORT.md).
