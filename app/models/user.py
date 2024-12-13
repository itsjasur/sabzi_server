import enum
from ..core.database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy import String, func, literal, text
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
    status: Mapped[UserStatus] = mapped_column(default=UserStatus.unverified)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_onupdate=func.now())


class UserVerification(Base):
    __tablename__ = "user_verifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(index=True)
    phone_number: Mapped[str] = mapped_column(String(10), index=True)
    verification_code: Mapped[str] = mapped_column(String(6))
    verification_token: Mapped[str] = mapped_column(String(50), comment="session identifier")
    verified_at: Mapped[datetime] = mapped_column(nullable=True)
    attempts: Mapped[int] = mapped_column(server_default=literal(5))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(server_onupdate=func.now() + text("interval '5 minutes'"))


# expires_at: Mapped[datetime] = mapped_column(server_onupdate=lambda: datetime.now(timezone.utc) + timedelta(minutes=5))
# .replace(microsecond=0)
