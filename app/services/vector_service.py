from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.channel_characteristics import Channel_charisteristic
from app.models.channels import Channel


@lru_cache(maxsize=1)
def _get_embedding_model() -> SentenceTransformer:
    # MatchmakingService is constructed per request, so cache the heavy model
    # to avoid loading BGE-M3 from disk repeatedly.
    return SentenceTransformer("BAAI/bge-m3")


class VectorService:
    """Create channel embeddings and search them in PostgreSQL with pgvector."""

    def __init__(self):
        # BGE-M3 returns 1,024-dimensional multilingual embeddings.
        self.embedding_model = _get_embedding_model()

    def _embed(self, text: str) -> list[float]:
        text = text.strip()
        if not text:
            raise ValueError("profile_text cannot be empty")
        return self.embedding_model.encode(text).tolist()

    def upsert_channel_profile(self, channel_id: str, profile_text: str, metadata: dict):
        """Insert or update the channel and its profile embedding."""
        clean_metadata = {
            "channel_title": str(metadata.get("channel_title", metadata.get("title", "Unknown"))),
            "category": str(metadata.get("category", "")),
            "subscriber_band": str(metadata.get("subscriber_band", "")),
            "content_style": str(metadata.get("content_style", "")),
            "key_topics": str(metadata.get("key_topics", "")),
            "avg_views": int(metadata.get("avg_views", 0) or 0),
        }
        embedding = self._embed(profile_text)

        with SessionLocal() as db:
            channel = db.scalar(
                select(Channel).where(Channel.channel_code == str(channel_id))
            )
            if channel is None:
                channel = Channel(
                    channel_code=str(channel_id),
                    channel_name=clean_metadata["channel_title"],
                )
                db.add(channel)
                db.flush()
            else:
                channel.channel_name = clean_metadata["channel_title"]

            characteristic = db.scalar(
                select(Channel_charisteristic).where(
                    Channel_charisteristic.channel_id == channel.id
                )
            )
            if characteristic is None:
                characteristic = Channel_charisteristic(channel_id=channel.id)
                db.add(characteristic)

            characteristic.channel_vector = embedding
            characteristic.profile_text = profile_text.strip()
            characteristic.category = clean_metadata["category"]
            characteristic.subscribe_band = clean_metadata["subscriber_band"]
            characteristic.content_style = clean_metadata["content_style"]
            characteristic.key_topics = clean_metadata["key_topics"]
            characteristic.avg_views = clean_metadata["avg_views"]
            db.commit()

    def find_similar_channels(self, profile_text: str, top_k: int = 5):
        """Return the nearest profiles by cosine similarity."""
        query_vector = self._embed(profile_text)
        distance = Channel_charisteristic.channel_vector.cosine_distance(query_vector)

        with SessionLocal() as db:
            rows = db.execute(
                select(Channel, Channel_charisteristic, distance.label("distance"))
                .join(
                    Channel_charisteristic,
                    Channel_charisteristic.channel_id == Channel.id,
                )
                .where(Channel_charisteristic.channel_vector.is_not(None))
                .order_by(distance)
                .limit(top_k)
            ).all()

        return [
            {
                "channel_id": channel.channel_code,
                "channel_title": channel.channel_name or "Unknown Channel",
                "category": characteristic.category or "",
                "subscriber_band": characteristic.subscribe_band or "",
                "avg_views": characteristic.avg_views or 0,
                "similarity_score": round(max(0.0, 1.0 - float(distance_value)), 2),
                "profile_summary": characteristic.profile_text,
            }
            for channel, characteristic, distance_value in rows
        ]
