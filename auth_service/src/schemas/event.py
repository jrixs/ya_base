from pydantic import BaseModel


class EventCreate(BaseModel):
    user_id: str
    user_agent: str
