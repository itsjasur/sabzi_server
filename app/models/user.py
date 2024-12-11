import enum
from ..core.database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class UserStatus(enum.Enum):
    active = "active"  # user verified
    inactive = "inactive"  # not yet verified user status
    suspended = "suspended"  # user is blocked


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    status: Mapped[UserStatus] = mapped_column(default=UserStatus.inactive)
