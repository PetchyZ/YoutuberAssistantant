from pydantic import BaseModel, ConfigDict

class VideoAdd(BaseModel):    # Data from Frontend to FastAPI
    video_code: str
    title: str

class VideoResponse(BaseModel):  # Data from FastAPI to Frontend
    id: int
    title: str
    video_code: str

    model_config = ConfigDict(from_attributes=True)

