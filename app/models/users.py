from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class AnalysisHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: str = Field(index=True)
    video_title: Optional[str] = None
    thumbnail_url: Optional[str] = None

    # Score evaluate
    thumbnail_score: Optional[float] = None
    video_retention_score: Optional[str] = None

    # Evaluation Summary
    ai_evaluation_summary: Optional[str] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

