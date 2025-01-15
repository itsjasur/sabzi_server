from datetime import datetime
import enum
from typing import Annotated, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserStatus(str, enum.Enum):
    unverified = "unverified"
    verified = "verified"
    suspended = "suspended"


class UserBase(BaseModel):
    username: str
    status: UserStatus
    joined_date: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
        json_encoders={ObjectId: str},
        ser_json=True,
    )


class UserCreate(UserBase):

    pass


class UserResponse(UserBase):
    id: ObjectId | None

    # id: Annotated[str, Field(alias="_id", validation_alias="_id")] | None = None  # Ensure alias matches MongoDB field name

    # @field_validator("id", mode="before")
    # def validate_object_id(cls, v):
    #     print("Raw value of _id:", v)  # Debugging line to inspect raw value
    #     if isinstance(v, ObjectId):
    #         return str(v)  # Convert ObjectId to string
    #     elif v is not None:
    #         raise ValueError("Not a valid ObjectId")
    #     return v
