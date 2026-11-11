from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Thumbnail(Base):
    __tablename__ = "thumbnails"
    id: Mapped[int] = mapped_column(
        primary_key = True,
        index = True
    )

    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.id"),
        nullable = False
    )

    image_path: Mapped[str] = mapped_column(
        String(255),
        nullable = False
    )

    strength_comments: Mapped[str] = mapped_column(
        String(255),
    )

    weakness_comments: Mapped[str] = mapped_column(
        String(255)
    )

    recommend_comments: Mapped[str] = mapped_column(
        String(255)
    )

    visual_clarity_score: Mapped[int] = mapped_column()
    text_readability_score: Mapped[int] = mapped_column()
    emotional_hook_score: Mapped[int] = mapped_column()
    


