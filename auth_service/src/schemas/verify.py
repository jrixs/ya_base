from pydantic import BaseModel


class VerifyToken(BaseModel):
    access_token: str
    role_name: str
    username: str
