from config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ✅ Create the SQLAlchemy engine with robust connection handling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # ✅ Check if connection is alive before using it
    pool_recycle=1800,        # ✅ Reconnect every 30 mins (avoids stale sockets)
    pool_size=10,             # ✅ Maintain up to 10 active connections
    max_overflow=5,           # ✅ Allow 5 extra during spikes
)

# ✅ Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ✅ Base class for all ORM models
Base = declarative_base()

# ✅ Dependency for getting a DB session
def get_db():
    """Yields a new SQLAlchemy session with proper cleanup."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()          # ✅ Rollback on error to keep session clean
        raise
    finally:
        db.close()
