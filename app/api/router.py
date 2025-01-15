from fastapi import APIRouter
from app.api import auth
from app.api import user
from app.api import my_listing
from app.api import public_listing
from app.api import test

api_router = APIRouter()
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
# api_router.include_router(my_listing.router, prefix="/my-listing", tags=["my-isting"])
# api_router.include_router(public_listing.router, prefix="/public-listing", tags=["public-listing"])
# api_router.include_router(test.router, prefix="/test", tags=["test"])
