from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from config import SQLALCHEMY_DATABASE_URL

# Configure the engine with explicit pool settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,        # Moderate pool size for t3.small
    max_overflow=20,     # Allow more overflow connections
    pool_timeout=30,     # Standard timeout is sufficient
    pool_pre_ping=True,  # Keep connection health checks
    pool_recycle=3600,   # 1 hour recycle is fine with more memory
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()