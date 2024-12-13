from fastapi import APIRouter
from app.api import auth
from app.api import user
from app.api import item

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(item.router, prefix="/items", tags=["items"])
