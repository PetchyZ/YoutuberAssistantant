from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import performance, thumbnail_analytics, trend, matchmaking, video_quality

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.models.users import User
from app.database import create_db_and_tables

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Backend API for AI Content Creator Assistant"
)

# Include Routers
app.include_router(thumbnail_analytics.router, prefix="/api/v1/thumbnail", tags=["Analytics"])
app.include_router(performance.router, prefix="/api/v1/performance", tags=["Performance Driver Analysis"])
app.include_router(video_quality.router, prefix="/api/v1/video-quality", tags=["Video quality analytics"])
app.include_router(trend.router, prefix="/api/v1/trend", tags=["Trending Analytics"])
app.include_router(matchmaking.router, prefix="/api/v1/matchmaking", tags=["Matchmaking Player"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shiny-sable-2c18fb.netlify.app", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    stmt = select(User)
    result =  db.execute(stmt)
    users = result.scalars().all()
    return users

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
