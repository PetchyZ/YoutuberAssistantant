from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Trend(Base):
    __tablename__ = "trends"
    id: Mapped[int] = mapped_column(
        primary_key = True,
        index = True
    )

    channel_id: Mapped[int] = mapped_column(
        ForeignKey("channels.id"),
        nullable = False
    ) 

    recent_title: Mapped[str] = mapped_column(
        String(255),
    )

    top_market_title: Mapped[str] = mapped_column(
        String(255),
    )

    channel_velocity_summary: Mapped[str] = mapped_column(
        String(255)
    )

    emerging_topics: Mapped[str] = mapped_column(
        String(255)
    )

    content_gaps: Mapped[str] = mapped_column(
        String(255)
    )

    next_step_recommends: Mapped[str] = mapped_column(
        String(255)
    )
    
    market_velocity: Mapped[float] = mapped_column()
    avg_velocity: Mapped[float] = mapped_column()
    channel_velocity_score: Mapped[int] = mapped_column()


