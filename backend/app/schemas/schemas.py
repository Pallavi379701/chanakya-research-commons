from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr

# Auth & User
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: str = "student"
    department: str
    research_interests: Optional[str] = ""
    interest_tags: Optional[str] = ""
    bio: Optional[str] = ""
    publication_url: Optional[str] = ""

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(UserBase):
    id: int
    is_spam: bool
    created_at: datetime
    followers_count: Optional[int] = 0
    following_count: Optional[int] = 0

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# Papers & Library
class PaperBase(BaseModel):
    title: str
    abstract: Optional[str] = ""
    authors: Optional[str] = ""
    venue: Optional[str] = ""
    year: Optional[int] = 2024
    doi: Optional[str] = ""
    arxiv_id: Optional[str] = ""
    url: Optional[str] = ""
    source: Optional[str] = "arXiv"
    department: Optional[str] = "Computer Science"
    topics: Optional[str] = ""

class PaperCreate(PaperBase):
    pass

class PaperOut(PaperBase):
    id: int
    citation_count: int
    save_count: Optional[int] = 0
    sources: Optional[List[str]] = []
    pagerank_score: Optional[float] = 0.0
    created_at: datetime

    class Config:
        from_attributes = True

class LibraryItemCreate(BaseModel):
    paper_id: int
    notes: Optional[str] = ""
    collection_name: Optional[str] = "General"

class LibraryItemOut(BaseModel):
    id: int
    user_id: int
    paper_id: int
    notes: Optional[str]
    collection_name: str
    created_at: datetime
    paper: Optional[PaperOut] = None

    class Config:
        from_attributes = True

# Posts & Comments
class CommentCreate(BaseModel):
    content: str
    parent_comment_id: Optional[int] = None

class CommentOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    parent_comment_id: Optional[int]
    content: str
    created_at: datetime
    user: Optional[UserOut]

    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    title: str
    content: str
    tags: Optional[str] = ""
    attached_paper_id: Optional[int] = None

class PostOut(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    tags: str
    attached_paper_id: Optional[int]
    upvotes: int
    created_at: datetime
    author: Optional[UserOut]
    attached_paper: Optional[PaperOut]
    comments_count: Optional[int] = 0
    has_upvoted: Optional[bool] = False

    class Config:
        from_attributes = True

# Unified Search
class SearchResponse(BaseModel):
    query: str
    mode: str
    external_papers: List[Dict[str, Any]]
    chanakya_library: List[Dict[str, Any]]
    people: List[Dict[str, Any]]
    posts: List[Dict[str, Any]]
    total_matches: int

# Assistant Q&A (RAG)
class AssistantQuery(BaseModel):
    question: str
    top_k: Optional[int] = 5

class CitationPassage(BaseModel):
    paper_id: int
    title: str
    authors: str
    passage: str
    score: float
    citation_index: int

class AssistantResponse(BaseModel):
    question: str
    answer: str
    citations: List[CitationPassage]

# Trends & Anomaly
class SpikeAlert(BaseModel):
    topic: str
    current_count: int
    baseline_mean: float
    z_score: float
    severity: str
    detected_at: str

class TrendsResponse(BaseModel):
    trending_topics_7d: List[Dict[str, Any]]
    trending_topics_30d: List[Dict[str, Any]]
    active_spikes: List[SpikeAlert]
    spam_flags_count: int

# Evaluation Benchmark Response
class EvaluationMetric(BaseModel):
    feature: str
    method: str
    baseline: str
    metric_name: str
    metric_value: float
    baseline_value: float
    description: str

class BenchmarkReport(BaseModel):
    status: str
    timestamp: str
    metrics: List[EvaluationMetric]
    confusion_matrices: Dict[str, Any]
