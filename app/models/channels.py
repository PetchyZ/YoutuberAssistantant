from sqlalchemy import String, Integer, Column
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Channel(Base):
    __tablename__ = "channels"
    id: Mapped[int] = mapped_column(
        primary_key = True,
        index = True,
    )

    channel_code: Mapped[str] = mapped_column(
        String(255),
        unique = True,
        nullable = False
    )

    channel_name: Mapped[str] = mapped_column(
        String(255),
    )

    