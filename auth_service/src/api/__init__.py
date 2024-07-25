from fastapi import APIRouter, Depends

from src.api import (
    logout,
    not_auth,
    role,
    user_management,
    user,
    service_verify
)

from src.core.dependencies import verify_user_admin_rights, verify_user_access

# если юзер без авторизации
not_auth_router = APIRouter()
not_auth_router.include_router(not_auth.router, tags=["Not Auth"])

# если юзер авторизовался
auth_router = APIRouter(dependencies=[Depends(verify_user_access)])
auth_router.include_router(logout.router, tags=["Logout"])
auth_router.include_router(user.router, tags=["User"])

# апи для сервиса (пока без токена, но по идее должен быть токен взаимодействия между сервисами)
service_router = APIRouter()
service_router.include_router(service_verify.router, tags=["Service Token Verify"])

# если юзер суперюзер
admin_router = APIRouter(prefix="/admin", dependencies=[Depends(verify_user_admin_rights)])
admin_router.include_router(role.router, tags=["Admin Panel: roles"])
admin_router.include_router(user_management.router, tags=["Admin Panel: user management"])
