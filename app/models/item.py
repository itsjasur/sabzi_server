from datetime import datetime
import enum
from ..core.database import Base
from sqlalchemy.orm import Mapped
from typing import Optional
from sqlalchemy import DateTime, Float, func, literal, text
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class ItemStatus(enum.Enum):
    active = "active"
    sold = "sold"
    hidden = "hidden"
    deleted = "deleted"


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    price: Mapped[Optional[float]] = mapped_column()
    price_negotiable: Mapped[bool] = mapped_column(server_default=literal(True))

    status: Mapped[ItemStatus] = mapped_column(server_default=literal(ItemStatus.active.value))
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


class ItemImage(Base):
    __tablename__ = "item_images"
    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[Optional[int]] = mapped_column(index=True, nullable=True)
    key: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(56), default="local")  # server origin e.g google cloud, firebase inhouse server, etc....
    extension: Mapped[str] = mapped_column(String(16))
    bucket_path: Mapped[str] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
