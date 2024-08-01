from pydantic import BaseModel, ConfigDict


class RoleRequest(BaseModel):
    name: str
    create_access: bool
    update_access: bool
    view_access: bool
    delete_access: bool


class RoleResponse(RoleRequest):
    model_config = ConfigDict(from_attributes=True)
    id: str
