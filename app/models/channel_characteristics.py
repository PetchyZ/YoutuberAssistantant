from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.db.base import Base

class Channel_charisteristic(Base):
    __tablename__ = "channel_charisteristics"
    id: Mapped[int] = mapped_column(
        primary_key = True,
        index = True
    )

    channel_id: Mapped[int] = mapped_column(
        ForeignKey("channels.id"),
        nullable = False
    ) 

    channel_vector: Mapped[list[float]] = mapped_column(
       Vector(1024),
       nullable=True,
    )

    profile_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    category: Mapped[str] = mapped_column(
        String(300),
    )

    subscribe_band: Mapped[str] = mapped_column(
        String(300)
    )

    content_style: Mapped[str] = mapped_column(
        String(300)
    )

    key_topics: Mapped[str] = mapped_column(
        String(300)
    )
    
    avg_views: Mapped[float] = mapped_column()


