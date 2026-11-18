from pydantic import BaseModel, ConfigDict

class TrendAdd(BaseModel):    # Data from Frontend to FastAPI
    channel_id: int
    channel_vector: list[float]
    category: str
    subscribe_band: str
    content_style: str
    key_topics: str
    avg_views: float

class TrendResponse(BaseModel):  # Data from FastAPI to Frontend
    id: int
    channel_id: int
    channel_vector: list[float]
    category: str
    subscribe_band: str
    content_style: str
    key_topics: str
    avg_views: float

    model_config = ConfigDict(from_attributes=True)

