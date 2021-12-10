from fastapi import APIRouter
from feed_management.authorization import route_login
from feed_management.users import route_users


api_router = APIRouter()
api_router.include_router(route_users.router, prefix="", tags=["users-webapp"])
api_router.include_router(route_login.router, prefix="", tags=["authorization-webapp"])
