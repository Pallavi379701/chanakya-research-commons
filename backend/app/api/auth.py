import hashlib
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.models import User, Follow, TopicFollow
from app.schemas.schemas import UserCreate, UserLogin, UserOut, TokenResponse

router = APIRouter(prefix="/auth", tags=["F1: Accounts & Profiles"])

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.username == user_in.username) | (User.email == user_in.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_pw(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        department=user_in.department,
        research_interests=user_in.research_interests or "",
        interest_tags=user_in.interest_tags or "",
        bio=user_in.bio or "",
        publication_url=user_in.publication_url or ""
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or user.hashed_password != hash_pw(login_data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Calculate follow counts
    followers_count = db.query(Follow).filter(Follow.following_id == user.id).count()
    following_count = db.query(Follow).filter(Follow.follower_id == user.id).count()

    user_out = UserOut.model_validate(user)
    user_out.followers_count = followers_count
    user_out.following_count = following_count

    return TokenResponse(
        access_token=f"token_user_{user.id}_{user.username}",
        token_type="bearer",
        user=user_out
    )

@router.get("/users", response_model=List[UserOut])
def list_users(department: Optional[str] = None, role: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(User).filter(User.is_spam == False)
    if department:
        q = q.filter(User.department == department)
    if role:
        q = q.filter(User.role == role)
    users = q.limit(limit).all()
    
    res = []
    for u in users:
        u_out = UserOut.model_validate(u)
        u_out.followers_count = db.query(Follow).filter(Follow.following_id == u.id).count()
        u_out.following_count = db.query(Follow).filter(Follow.follower_id == u.id).count()
        res.append(u_out)
    return res

@router.get("/users/{user_id}", response_model=UserOut)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    u_out = UserOut.model_validate(user)
    u_out.followers_count = db.query(Follow).filter(Follow.following_id == user.id).count()
    u_out.following_count = db.query(Follow).filter(Follow.follower_id == user.id).count()
    return u_out

@router.post("/follow/{target_user_id}")
def follow_user(target_user_id: int, current_user_id: int = 1, db: Session = Depends(get_db)):
    if target_user_id == current_user_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    existing = db.query(Follow).filter(Follow.follower_id == current_user_id, Follow.following_id == target_user_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"action": "unfollowed", "target_user_id": target_user_id}
    else:
        new_follow = Follow(follower_id=current_user_id, following_id=target_user_id)
        db.add(new_follow)
        db.commit()
        return {"action": "followed", "target_user_id": target_user_id}

@router.post("/follow-topic")
def follow_topic(topic: str, current_user_id: int = 1, db: Session = Depends(get_db)):
    existing = db.query(TopicFollow).filter(TopicFollow.user_id == current_user_id, TopicFollow.topic == topic).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"action": "unfollowed_topic", "topic": topic}
    else:
        new_tf = TopicFollow(user_id=current_user_id, topic=topic)
        db.add(new_tf)
        db.commit()
        return {"action": "followed_topic", "topic": topic}
