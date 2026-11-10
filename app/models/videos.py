from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class video(Base):
    __tablename__ = "videos"
    id: Mapped[int] = mapped_column(
        primary_key = True,
        index = True
    )

    title: Mapped[str] = mapped_column(
        String(255)
    )

    video_code: Mapped[str] = mapped_column(
        String(30),
        unique = True
    )


