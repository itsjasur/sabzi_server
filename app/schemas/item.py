from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.item import ItemStatus


# base schema with common attributes
class ItemBase(BaseModel):
    key: str = Field(..., min_length=1, max_length=50)
    price: Optional[float] = None
    price_negotiable: bool = True
    category_id: int
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    latitude: float = Field(..., ge=-90, le=90, description="Latitude between -90 and 90")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude between -180 and 180")


# schema for creating a new item
class ItemCreate(ItemBase):
    pass


# schema for updating an existing item
class ItemUpdate(BaseModel):
    key: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[float] = None
    price_negotiable: Optional[bool] = None
    status: Optional[ItemStatus] = None
    category_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude between -90 and 90")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude between -180 and 180")


# schema for reading an item (response model)
class ItemResponse(ItemBase):
    id: int
    status: ItemStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True