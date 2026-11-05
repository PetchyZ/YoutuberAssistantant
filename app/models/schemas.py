from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):    # Data from Frontend to FastAPI
    username: str
    email: str

class UserResponse(BaseModel):  # Data from FastAPI to Frontend
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)

