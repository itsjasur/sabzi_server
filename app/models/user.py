from datetime import datetime, timezone
import enum
from typing import Annotated, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class UserStatus(str, enum.Enum):
    unverified = "unverified"
    verified = "verified"
    suspended = "suspended"


class UserBase(BaseModel):
    username: str
    status: UserStatus
    joined_date: datetime
    is_agree_to_marketing_terms: bool

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
        json_encoders={ObjectId: str},
        ser_json=True,
    )


class User(BaseModel):
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    username: Optional[str] = None
    phone_number: str
    status: UserStatus
    joined_date: datetime
    is_agree_to_marketing_terms: bool

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
        json_encoders={ObjectId: str},
        ser_json=True,
    )

    def model_json(self):
        return self.model_dump(mode="json")


class UserResponse(BaseModel):
    id: str
    username: str
    phone_number: str
    status: UserStatus
    joined_date: datetime
    is_agree_to_marketing_terms: bool

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    def from_mongo_doc(self):
        return self.model_dump()

    @model_validator(mode="before")
    def validate_object_id(cls, data: any) -> any:
        if isinstance(data, dict) and "_id" in data and isinstance(data["_id"], ObjectId):
            data["id"] = str(data["_id"])
        return data


class Verification(BaseModel):
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    created_date: datetime
    user_id: Optional[ObjectId] = None
    phone_number: str
    code: int
    token: Optional[str] = None  # secrets.token_hex(16)
    attempts: int

    @field_validator("created_date")
    def ensure_timezone(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
        json_encoders={ObjectId: str},
        ser_json=True,
    )
