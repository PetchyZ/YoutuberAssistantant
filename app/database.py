from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# 1. Database Engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping = True
)

# 2. Session Factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)

# 3. Base Model
class Base(DeclarativeBase):
    pass

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

# 4. Database Dependency
def get_db():
    with SessionLocal() as db:
        yield db
        
