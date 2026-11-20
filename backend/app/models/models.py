from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(String(50), default="student", index=True)  # student, faculty, researcher, admin
    department = Column(String(100), index=True)
    research_interests = Column(Text, default="")
    interest_tags = Column(String(255), default="")  # comma separated
    bio = Column(Text, default="")
    publication_url = Column(String(255), default="")
    is_spam = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    library_items = relationship("LibraryItem", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")

class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), index=True)
    following_id = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class TopicFollow(Base):
    __tablename__ = "topic_follows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    topic = Column(String(100), index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), index=True, nullable=False)
    abstract = Column(Text, default="")
    authors = Column(Text, default="")
    venue = Column(String(200), default="")
    year = Column(Integer, default=2024, index=True)
    doi = Column(String(150), index=True, default="")
    arxiv_id = Column(String(100), index=True, default="")
    url = Column(String(300), default="")
    source = Column(String(50), default="arXiv", index=True)  # arXiv, OpenAlex, Semantic Scholar, RSS
    department = Column(String(100), index=True, default="Computer Science")
    topics = Column(String(255), default="")  # comma separated
    citation_count = Column(Integer, default=0, index=True)
    raw_bronze_id = Column(String(100), default="")
    is_duplicate_planted = Column(Boolean, default=False)
    duplicate_of_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    library_entries = relationship("LibraryItem", back_populates="paper")

class PaperCitation(Base):
    __tablename__ = "paper_citations"

    id = Column(Integer, primary_key=True, index=True)
    source_paper_id = Column(Integer, ForeignKey("papers.id"), index=True)
    target_paper_id = Column(Integer, ForeignKey("papers.id"), index=True)

class LibraryItem(Base):
    __tablename__ = "library_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), index=True)
    notes = Column(Text, default="")
    collection_name = Column(String(100), default="General", index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="library_items")
    paper = relationship("Paper", back_populates="library_entries")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String(255), default="")  # comma separated
    attached_paper_id = Column(Integer, ForeignKey("papers.id"), nullable=True)
    upvotes = Column(Integer, default=0, index=True)
    is_spam = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    author = relationship("User", back_populates="posts")
    attached_paper = relationship("Paper")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    content = Column(Text, nullable=False)
    is_spam = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

class PostUpvote(Base):
    __tablename__ = "post_upvotes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    event_type = Column(String(50), index=True)  # save, view, search, post, comment
    target_id = Column(Integer, nullable=True)
    query = Column(String(255), nullable=True)
    department = Column(String(100), nullable=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
