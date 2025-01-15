# from pydantic import BaseModel, Field
# from datetime import datetime
# from typing import Optional

# from sqlalchemy import Sequence
# from app.models.listing import Listing, ListingImage, ListingStatus


# class ListingAddRequest(BaseModel):
#     price: Optional[float] = Field(default=None, ge=0)
#     price_negotiable: bool = True
#     category_id: int = Field(..., ge=0)
#     image_keys: list[str] = []
#     title: str = Field(..., min_length=1, max_length=100)
#     description: str = Field(..., min_length=1, max_length=500)
#     latitude: float = Field(..., ge=-90, le=90, description="Latitude between -90 and 90")
#     longitude: float = Field(..., ge=-180, le=180, description="Longitude between -180 and 180")


# class ListingUpdateRequest(BaseModel):
#     listing_key: str
#     price: Optional[float] = Field(default=None, gt=0)
#     price_negotiable: bool = True
#     category_id: int = Field(..., ge=0)
#     image_keys: Optional[list[str]] = Field(default=[])
#     title: str = Field(..., min_length=1, max_length=100)
#     description: str = Field(..., min_length=1, max_length=500)


# class ListingStatusChange(BaseModel):
#     listing_key: str
#     status: ListingStatus
#     buyer_key: Optional[str] = None


# class ListingImageInfo(BaseModel):
#     key: str
#     url: str

#     @classmethod
#     def from_db_model(cls, image: ListingImage) -> "ListingImageInfo":
#         return cls(
#             key=image.key,
#             url=f"{image.storage_source}/{image.storage_bucket}/{image.key}{image.extension}",
#         )


# class ListingInfo(BaseModel):
#     key: str
#     images: list[ListingImageInfo]
#     price: float | None
#     price_negotiable: bool
#     category_id: int
#     title: str
#     description: str

#     @classmethod
#     def from_db_models(cls, listing: Listing, images: Sequence[ListingImage] | None) -> "ListingInfo":
#         return cls(
#             key=listing.key,
#             images=[ListingImageInfo.from_db_model(image) for image in (images or [])],
#             price=listing.price,
#             price_negotiable=listing.price_negotiable,
#             category_id=listing.category_id,
#             title=listing.title,
#             description=listing.description,
#         )
