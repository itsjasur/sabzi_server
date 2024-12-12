from pydantic import BaseModel, Field
from app.models.user import UserStatus


class UserInfo(BaseModel):
    id: int


# for updating user information
class UserPhoneNumberUpdate(BaseModel):
    id: int
    phone_number: str = Field(..., min_length=1, max_length=10)


# for returning user information
class UserResponse(BaseModel):
    id: int
    username: str | None
    phone_number: str
    status: UserStatus

    class Config:
        from_attributes = True
