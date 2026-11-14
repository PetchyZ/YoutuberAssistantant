from pydantic import BaseModel, ConfigDict

class VideoQualityAdd(BaseModel):    # Data from Frontend to FastAPI
    video_id: int
    performance_summary: str
    audience_positive_comments: str
    audience_negative_comments: str
    strength_comments: str
    weakness_comments: str
    recommend_comments: str
    performance_score: int

class VideoQualityResponse(BaseModel):  # Data from FastAPI to Frontend
    id: int
    video_id: int
    performance_summary: str
    audience_positive_comments: str
    audience_negative_comments: str
    strength_comments: str
    weakness_comments: str
    recommend_comments: str
    performance_score: int

    model_config = ConfigDict(from_attributes=True)

