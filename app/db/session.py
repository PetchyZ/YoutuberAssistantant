from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def create_db_and_tables() -> None:
    # Import models so their tables are registered on Base.metadata.
    Base.metadata.create_all(bind=engine)


def get_db():
    with SessionLocal() as db:
        yield db
