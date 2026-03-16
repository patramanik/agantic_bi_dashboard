import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .models import Base
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Database URL resolution ────────────────────────────────────────────────────
_pg_url = os.getenv("DATABASE_URL")

def _try_postgres(url: str):
    """Return a working PostgreSQL engine or None on failure."""
    try:
        eng = create_engine(url, pool_pre_ping=True)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Connected to PostgreSQL: %s", url.split("@")[-1])
        return eng
    except Exception as exc:
        logger.warning("PostgreSQL unavailable (%s) – falling back to SQLite.", exc)
        return None

def _sqlite_engine():
    """Return a SQLite engine stored next to this file's package root."""
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "app.db")
    db_path = os.path.abspath(db_path)
    url = f"sqlite:///{db_path}"
    logger.info("Using SQLite database at: %s", db_path)
    return create_engine(url, connect_args={"check_same_thread": False})

# ── Engine selection ───────────────────────────────────────────────────────────
if _pg_url:
    engine = _try_postgres(_pg_url) or _sqlite_engine()
else:
    logger.info("DATABASE_URL not set – using SQLite fallback.")
    engine = _sqlite_engine()

# ── Session factory ────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables (safe to call on every startup)."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
