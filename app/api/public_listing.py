# from typing import Optional
# from fastapi import APIRouter
# from pydantic import BaseModel, Field

# from app.core.database import db_conn
# from app.core.utils.auth import AUTH_ME
# from app.schemas.listing import ListingInfo


# router = APIRouter()


# class ListingInfo(BaseModel):
#     search_key: Optional[str]
#     category_id: int = Field(default=0, ge=0)


# @router.post("/fetch-listings", response_model=ListingInfo, description="Adds new listing image")
# def fetch_listings(
#     user: AUTH_ME,
#     db: db_conn,
# ):
#     pass
