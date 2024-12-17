from datetime import datetime
import enum
from ..core.database import Base
from sqlalchemy.orm import Mapped
from typing import Optional
from sqlalchemy import DateTime, Float, literal, text
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class ListingStatus(enum.Enum):
    active = "active"
    sold = "sold"
    hidden = "hidden"
    deleted = "deleted"


class Listing(Base):
    __tablename__ = "listings"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    price: Mapped[Optional[float]] = mapped_column()
    price_negotiable: Mapped[bool] = mapped_column(server_default=literal(True))
    status: Mapped[ListingStatus] = mapped_column(server_default=literal(ListingStatus.active.value))
    category_id: Mapped[int] = mapped_column(index=True)  # from categories table, but not foreign key
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(String(1024))
    user_id: Mapped[int] = mapped_column(index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP")
    )


class ListingImage(Base):
    __tablename__ = "listing_images"
    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[Optional[int]] = mapped_column(index=True, nullable=True)
    key: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    extension: Mapped[str] = mapped_column(String(16))
    storage_source: Mapped[str] = mapped_column(String(512))
    storage_bucket: Mapped[str] = mapped_column(String(512))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
