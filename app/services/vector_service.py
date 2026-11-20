from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.channel_characteristics import Channel_charisteristic
from app.models.channels import Channel


@lru_cache(maxsize=1)
def _get_embedding_model() -> SentenceTransformer:
    # MatchmakingService is created per request, so keep the heavy model cached.
    return SentenceTransformer("BAAI/bge-m3")


class VectorService:
    """Create embeddings and search channel profiles with pgvector."""

    def __init__(self):
        self.embedding_model = _get_embedding_model()

    def embed_text(self, text: str) -> list[float]:
        """Convert profile or query text to a 1,024-dimensional BGE-M3 vector."""
        normalized_text = text.strip()
        if not normalized_text:
            raise ValueError("text cannot be empty")
        return self.embedding_model.encode(normalized_text).tolist()

    def find_similar_channels(self, profile_text: str, top_k: int = 5):
        """Return channel profiles ranked by cosine similarity to the text."""
        query_vector = self.embed_text(profile_text)
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
