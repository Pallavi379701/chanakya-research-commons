from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.models import Post, Comment, PostUpvote, User, Paper, Follow, TopicFollow, EventLog
from app.schemas.schemas import PostCreate, PostOut, CommentCreate, CommentOut

router = APIRouter(prefix="/posts", tags=["F2: Posts & Discussions"])

@router.get("", response_model=List[PostOut])
def list_posts(
    tag: Optional[str] = None,
    user_id: Optional[int] = None,
    current_user_id: Optional[int] = 1,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    q = db.query(Post).filter(Post.is_spam == False)
    if tag:
        q = q.filter(Post.tags.contains(tag))
    if user_id:
        q = q.filter(Post.user_id == user_id)
    
    posts = q.order_by(Post.created_at.desc()).limit(limit).all()
    
    result = []
    for p in posts:
        has_upvoted = False
        if current_user_id:
            has_upvoted = db.query(PostUpvote).filter(PostUpvote.post_id == p.id, PostUpvote.user_id == current_user_id).first() is not None
        
        comments_cnt = db.query(Comment).filter(Comment.post_id == p.id).count()
        p_out = PostOut.model_validate(p)
        p_out.comments_count = comments_cnt
        p_out.has_upvoted = has_upvoted
        result.append(p_out)
    return result

@router.get("/feed", response_model=List[PostOut])
def get_personalized_feed(
    current_user_id: int = 1,
    limit: int = 40,
    db: Session = Depends(get_db)
):
    """
    Personalized Discussion Feed:
    Blends posts from followed members, followed topics, and top trending discussions.
    """
    # 1. Followed members
    followed_user_ids = [f.following_id for f in db.query(Follow.following_id).filter(Follow.follower_id == current_user_id).all()]
    
    # 2. Followed topics
    followed_topics = [t.topic.lower() for t in db.query(TopicFollow.topic).filter(TopicFollow.user_id == current_user_id).all()]

    all_posts = db.query(Post).filter(Post.is_spam == False).order_by(Post.created_at.desc()).limit(200).all()

    scored_posts = []
    for p in all_posts:
        score = 1.0  # base
        if p.user_id in followed_user_ids:
            score += 3.0
        
        post_tags = [t.strip().lower() for t in p.tags.split(",") if t.strip()]
        if any(ft in post_tags for ft in followed_topics):
            score += 2.5
        
        score += min(p.upvotes * 0.1, 2.0)

        has_upvoted = db.query(PostUpvote).filter(PostUpvote.post_id == p.id, PostUpvote.user_id == current_user_id).first() is not None
        comments_cnt = db.query(Comment).filter(Comment.post_id == p.id).count()

        p_out = PostOut.model_validate(p)
        p_out.comments_count = comments_cnt
        p_out.has_upvoted = has_upvoted
        scored_posts.append((score, p_out))

    scored_posts.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored_posts[:limit]]

@router.post("", response_model=PostOut)
def create_post(post_in: PostCreate, current_user_id: int = 1, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_post = Post(
        user_id=current_user_id,
        title=post_in.title,
        content=post_in.content,
        tags=post_in.tags or "",
        attached_paper_id=post_in.attached_paper_id,
        upvotes=0,
        is_spam=False
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # Log event
    db.add(EventLog(
        user_id=current_user_id,
        event_type="post",
        target_id=new_post.id,
        department=user.department,
        timestamp=datetime.now(timezone.utc)
    ))
    db.commit()

    p_out = PostOut.model_validate(new_post)
    p_out.comments_count = 0
    p_out.has_upvoted = False
    return p_out

@router.post("/{post_id}/upvote")
def toggle_upvote(post_id: int, current_user_id: int = 1, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing = db.query(PostUpvote).filter(PostUpvote.post_id == post_id, PostUpvote.user_id == current_user_id).first()
    if existing:
        db.delete(existing)
        post.upvotes = max(0, post.upvotes - 1)
        db.commit()
        return {"action": "unupvoted", "upvotes": post.upvotes}
    else:
        new_upvote = PostUpvote(post_id=post_id, user_id=current_user_id)
        db.add(new_upvote)
        post.upvotes += 1
        db.commit()
        return {"action": "upvoted", "upvotes": post.upvotes}

@router.get("/{post_id}/comments", response_model=List[CommentOut])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()
    return comments

@router.post("/{post_id}/comments", response_model=CommentOut)
def add_comment(post_id: int, comment_in: CommentCreate, current_user_id: int = 1, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment = Comment(
        post_id=post_id,
        user_id=current_user_id,
        parent_comment_id=comment_in.parent_comment_id,
        content=comment_in.content,
        is_spam=False
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    # Log event
    user = db.query(User).filter(User.id == current_user_id).first()
    db.add(EventLog(
        user_id=current_user_id,
        event_type="comment",
        target_id=post_id,
        department=user.department if user else None,
        timestamp=datetime.now(timezone.utc)
    ))
    db.commit()

    return new_comment
