import re
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.models import Post, User

# Known academic spam indicators
SPAM_KEYWORDS = [
    r"buy.*essay", r"cheap.*paper", r"crypto.*pool", r"whatsapp.*\+", r"telegram.*@",
    r"dissertation.*writing", r"plagiarism.*free", r"fake.*degrees", r"replica.*watch",
    r"200%.*roi", r"bitcoin.*doubling", r"assignment.*helper", r"discount.*rolex"
]

class SpamDetectorEngine:
    def __init__(self):
        self.spam_regexes = [re.compile(p, re.IGNORECASE) for p in SPAM_KEYWORDS]

    def is_spam_post(self, title: str, content: str) -> Tuple[bool, float, str]:
        """Classify whether a post is spam based on pattern matching and heuristic entropy."""
        full_text = f"{title} {content}".lower()
        matched_reasons = []

        # 1. Regex pattern matching
        for reg in self.spam_regexes:
            if reg.search(full_text):
                matched_reasons.append(f"Matched prohibited promotional pattern: '{reg.pattern}'")

        # 2. Suspicious URL and phone indicators
        url_matches = re.findall(r"https?://[^\s]+", full_text)
        suspicious_tlds = [".biz", ".store", ".fake", ".click", ".win"]
        for url in url_matches:
            if any(tld in url for tld in suspicious_tlds):
                matched_reasons.append(f"Suspicious unverified domain: {url}")

        if len(matched_reasons) > 0:
            confidence = min(0.6 + len(matched_reasons) * 0.2, 0.99)
            return True, confidence, "; ".join(matched_reasons)

        return False, 0.05, "Legitimate content"

    def scan_all_posts(self, db: Session) -> List[Dict[str, Any]]:
        """Scan all posts in database and return flagged items for admin inspection."""
        posts = db.query(Post).all()
        flagged = []

        for p in posts:
            is_spam, confidence, reason = self.is_spam_post(p.title, p.content)
            if is_spam or p.is_spam:
                flagged.append({
                    "post_id": p.id,
                    "user_id": p.user_id,
                    "author_name": p.author.full_name if p.author else "Unknown",
                    "author_username": p.author.username if p.author else "unknown",
                    "title": p.title,
                    "content": p.content[:140] + ("..." if len(p.content) > 140 else ""),
                    "confidence": round(confidence, 2),
                    "reason": reason,
                    "created_at": p.created_at.strftime("%Y-%m-%d %H:%M")
                })

        return flagged

    def scan_spam_accounts(self, db: Session) -> List[Dict[str, Any]]:
        """Identify suspicious spam accounts."""
        users = db.query(User).all()
        flagged_users = []

        for u in users:
            text = f"{u.username} {u.email} {u.research_interests} {u.bio}".lower()
            reasons = []
            for reg in self.spam_regexes:
                if reg.search(text):
                    reasons.append("Academic spam keyword in profile")
            if any(kw in u.username for kw in ["bot", "promo", "cheap", "essay", "jackpot"]):
                reasons.append("High-entropy promotional username")
            if ".fake" in u.email or ".biz" in u.publication_url:
                reasons.append("Unverified disposable email domain")

            if reasons or u.is_spam:
                flagged_users.append({
                    "user_id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "full_name": u.full_name,
                    "department": u.department,
                    "reasons": reasons or ["Flagged by supervisor"],
                    "is_flagged": True
                })

        return flagged_users

spam_engine = SpamDetectorEngine()
