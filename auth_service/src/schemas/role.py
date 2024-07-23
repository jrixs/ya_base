from pydantic import BaseModel


class RoleRequest(BaseModel):
    name: str


class RoleResponse(RoleRequest):
    id: int
