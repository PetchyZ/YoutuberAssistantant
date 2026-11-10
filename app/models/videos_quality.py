from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class video_quality(Base):
    __tablename__ = "videos_quality"
    id: Mapped[int] = mapped_column(
        primary_key = True,
        index = True
    )

    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.id"),
        nullable = False
    )

    performance_summary: Mapped[str] = mapped_column(
        String(255),
        nullable = False
    )

    audience_positive_comments: Mapped[str] = mapped_column(
        String(255),
    )

    audience_negative_comments: Mapped[str] = mapped_column(
        String(255)
    )

    strength_comments: Mapped[str] = mapped_column(
        String(255)
    )

    weakness_comments: Mapped[str] = mapped_column(
        String(255)
    )

    recommend_comments: Mapped[str] = mapped_column(
        String(255)
    )

    performance_score: Mapped[int] = mapped_column()