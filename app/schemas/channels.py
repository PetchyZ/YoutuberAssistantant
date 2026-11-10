from pydantic import BaseModel, ConfigDict

class ChannelAdd(BaseModel):    # Data from Frontend to FastAPI
    channel_code: str
    channel_name: str

class ChannelResponse(BaseModel):  # Data from FastAPI to Frontend
    id: int
    channel_code: str
    channel_name: str

    model_config = ConfigDict(from_attributes=True)

