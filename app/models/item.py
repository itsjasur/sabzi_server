from datetime import datetime
import enum
from ..core.database import Base
from sqlalchemy.orm import Mapped
from typing import Optional
from sqlalchemy import DECIMAL, func
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
    price: Mapped[Optional[float]]
    price_negotiable: Mapped[bool] = mapped_column(insert_default=True)
    status: Mapped[ItemStatus] = mapped_column(insert_default=ItemStatus.active)

    category_id: Mapped[int] = mapped_column(index=True)  # from categories table, but not foreign key

    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))

    user_id: Mapped[int] = mapped_column(index=True)

    latitude: Mapped[float] = mapped_column(DECIMAL(10, 8))  # -90 to 90
    longitude: Mapped[float] = mapped_column(DECIMAL(11, 8))  # -180 to 180

    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now())


class ItemImages(Base):
    __tablename__ = "item_images"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    item_id: Mapped[int] = mapped_column(index=True)
    filename: Mapped[str] = mapped_column(String(512))
    source: Mapped[str] = mapped_column(String(50), insert_default="server")  # server origin e.g google cloud, firebase inhouse server, etc....
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
