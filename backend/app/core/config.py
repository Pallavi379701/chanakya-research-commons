import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LAKEHOUSE_DIR = DATA_DIR / "lakehouse"
BRONZE_DIR = LAKEHOUSE_DIR / "bronze"
SILVER_DIR = LAKEHOUSE_DIR / "silver"
GOLD_DIR = LAKEHOUSE_DIR / "gold"
GROUND_TRUTH_FILE = DATA_DIR / "ground_truth_planted.json"

for d in [DATA_DIR, LAKEHOUSE_DIR, BRONZE_DIR, SILVER_DIR, GOLD_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'chanakya.db'}")
SECRET_KEY = os.getenv("SECRET_KEY", "chanakya-secret-key-2026-dw-mini-project")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

DEPARTMENTS = [
    "Computer Science",
    "Data Science & AI",
    "Electrical Engineering",
    "Biotechnology",
    "Mathematics & Computing",
    "School of Management"
]

ROLES = ["student", "faculty", "researcher", "admin"]
