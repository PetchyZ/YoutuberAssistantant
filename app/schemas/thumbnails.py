from pydantic import BaseModel, ConfigDict

class ThumbnailAdd(BaseModel):    # Data from Frontend to FastAPI
    video_id: int
    image_path: str
    strength_comments: str
    weakness_comments: str
    recommend_comments: str
    visual_clarity_score: int
    text_readability_score: int
    emotional_hook_score: int

class ThumbnailResponse(BaseModel):  # Data from FastAPI to Frontend
    id: int
    video_id: int
    image_pth: str
    strength_comments: str
    weakness_comments: str
    recommend_comments: str
    visual_clarity_score: int
    text_readability_score: int
    emotional_hook_score: int

    model_config = ConfigDict(from_attributes=True)

