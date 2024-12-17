from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.listing import ListingStatus


class ListingAddRequest(BaseModel):
    price: Optional[float] = Field(default=None, ge=0)
    price_negotiable: bool = True
    category_id: int
    image_keys: list[str] = []
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    latitude: float = Field(..., ge=-90, le=90, description="Latitude between -90 and 90")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude between -180 and 180")


class ListingUpdateRequest(BaseModel):
    listing_key: str
    price: Optional[float] = Field(default=None, gt=0)
    price_negotiable: bool = True
    category_id: int
    image_keys: list[str] = []
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)


class ListingStatusChange(BaseModel):
    listing_key: str
    status: ListingStatus
    buyer_key: Optional[str] = None


class ListingImageResponse(BaseModel):
    key: str
    url: str
    extension: str
