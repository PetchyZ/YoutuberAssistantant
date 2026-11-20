from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.channel_characteristics import Channel_charisteristic
from app.models.channels import Channel
from app.services.vector_service import VectorService


class ChannelProfileService:
    """Persist channel metadata and its generated embedding together."""

    def __init__(self, vector_service: VectorService | None = None):
        self.vector_service = vector_service or VectorService()

    def upsert_channel_profile(
        self,
        channel_id: str,
        profile_text: str,
        metadata: dict,
    ) -> None:
        """Create or update a channel and its profile in one database transaction."""
        channel_id = str(channel_id).strip()
        profile_text = profile_text.strip()
        if not channel_id:
            raise ValueError("channel_id cannot be empty")
        if not profile_text:
            raise ValueError("profile_text cannot be empty")

        channel_title = str(metadata.get("channel_title") or metadata.get("title") or "Unknown")[:255]
        category = str(metadata.get("category") or "")[:300]
        subscriber_band = str(metadata.get("subscriber_band") or "")[:300]
        content_style = str(metadata.get("content_style") or "")[:300]
        key_topics = str(metadata.get("key_topics") or "")[:300]
        embedding = self.vector_service.embed_text(profile_text)

        with SessionLocal() as db:
            channel = db.scalar(
                select(Channel).where(Channel.channel_code == channel_id)
            )
            if channel is None:
                channel = Channel(
                    channel_code=channel_id,
                    channel_name=channel_title,
                )
                db.add(channel)
                db.flush()
            else:
                channel.channel_name = channel_title

            characteristic = db.scalar(
                select(Channel_charisteristic).where(
                    Channel_charisteristic.channel_id == channel.id
                )
            )
            if characteristic is None:
                characteristic = Channel_charisteristic(channel_id=channel.id)
                db.add(characteristic)

            characteristic.channel_vector = embedding
            characteristic.profile_text = profile_text
            characteristic.category = category
            characteristic.subscribe_band = subscriber_band
            characteristic.content_style = content_style
            characteristic.key_topics = key_topics
            characteristic.avg_views = int(metadata.get("avg_views", 0) or 0)

            db.commit()
