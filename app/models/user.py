import enum
from typing import Optional
from ..core.database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy import DateTime, Float, String, func, literal, text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import datetime


class UserStatus(enum.Enum):
    verified = "verified"  # user verified
    unverified = "unverified"  # not yet verified user status
    suspended = "suspended"  # user is blocked


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    status: Mapped[UserStatus] = mapped_column(server_default=literal(UserStatus.unverified.value))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP")
    )
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)


class UserVerification(Base):
    __tablename__ = "user_verifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(index=True)
    phone_number: Mapped[str] = mapped_column(String(10), index=True)
    verification_code: Mapped[str] = mapped_column(String(6))
    verification_token: Mapped[str] = mapped_column(String(50), comment="session identifier")
    verified_at: Mapped[Optional[datetime]] = mapped_column()
    attempts: Mapped[int] = mapped_column(server_default=literal(5))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP + INTERVAL '5 minutes'"))


# expires_at: Mapped[datetime] = mapped_column(server_onupdate=text("CURRENT_TIMESTAMP") + text("interval '5 minutes'"))
# expires_at: Mapped[datetime] = mapped_column(server_onupdate=lambda: datetime.now(timezone.utc) + timedelta(minutes=5))
# .replace(microsecond=0)
