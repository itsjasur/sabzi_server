from pydantic import BaseModel, Field
from typing import Optional
from app.models.user import UserStatus


# for creating a new user
class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    phone_number: str = Field(..., min_length=10, max_length=15)
    status: UserStatus = Field(default=UserStatus.active)


# for returning user information
class UserResponse(BaseModel):
    id: int
    username: str
    phone_number: str
    status: UserStatus

    class Config:
        from_attributes = True


# for updating user information
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15)
    status: Optional[UserStatus] = None
