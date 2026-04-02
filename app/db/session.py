from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Update this engine block:
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # <-- 1. Tests connection before using it (Fixes EOF error)
    pool_recycle=300,    # <-- 2. Refreshes connections every 5 minutes (Great for Neon)
    # connect_args={"sslmode": "require"} # Keep this if you already had it!
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
