from pydantic import BaseModel, ConfigDict

class TrendAdd(BaseModel):    # Data from Frontend to FastAPI
    channel_id: int
    recent_title: str
    top_market_title: str
    channel_velocity_summary: str
    emerging_topics: str
    content_gaps: str
    next_step_recommends: str

class TrendResponse(BaseModel):  # Data from FastAPI to Frontend
    id: int
    channel_id: int
    recent_title: str
    top_market_title: str
    channel_velocity_summary: str
    emerging_topics: str
    content_gaps: str
    next_step_recommends: str

    model_config = ConfigDict(from_attributes=True)

