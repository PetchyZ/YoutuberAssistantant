from sqlalchemy import JSON, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Video_quality(Base):
    __tablename__ = "videos_quality"
    id: Mapped[int] = mapped_column(
        primary_key = True,
        index = True
    )

    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.id"),
        nullable = False
    )

    performance_summary: Mapped[list[str]] = mapped_column(
        String(1000),
        nullable = False
    )

    audience_positive_comments: Mapped[list[str]] = mapped_column(
        JSON,
    )

    audience_negative_comments: Mapped[list[str]] = mapped_column(
        JSON,
    )

    strength_comments: Mapped[list[str]] = mapped_column(
        JSON,
    )

    weakness_comments: Mapped[list[str]] = mapped_column(
        JSON,
    )

    recommend_comments: Mapped[list[str]] = mapped_column(
        JSON,
    )

    performance_score: Mapped[int] = mapped_column()