import enum
from ..core.database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy import DateTime, String, func, text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import datetime, timedelta, timezone


class UserStatus(enum.Enum):
    verified = "verified"  # user verified
    unverified = "unverified"  # not yet verified user status
    suspended = "suspended"  # user is blocked


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    status: Mapped[UserStatus] = mapped_column(insert_default=UserStatus.unverified)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now())


class UserVerification(Base):
    __tablename__ = "user_verifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(index=True)
    phone_number: Mapped[str] = mapped_column(String(10), index=True)
    verification_code: Mapped[str] = mapped_column(String(6))
    verification_token: Mapped[str] = mapped_column(String(50), comment="session identifier")
    verified_at: Mapped[datetime] = mapped_column(nullable=True)
    attempts: Mapped[int] = mapped_column(insert_default=5)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(insert_default=lambda: datetime.now(timezone.utc) + timedelta(minutes=5))


# .replace(microsecond=0)
