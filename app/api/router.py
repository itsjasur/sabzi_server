from fastapi import APIRouter
from app.api import auth
from app.api import user
from app.api import listing
from app.api import test

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(listing.router, prefix="/listings", tags=["listings"])
api_router.include_router(test.router, prefix="/test", tags=["test"])
