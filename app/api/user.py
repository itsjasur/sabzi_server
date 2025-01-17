from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.database import Database, get_database
from app.models.user import User, UserResponse, UserStatus
from app.repositories.user import UserRepository


router = APIRouter()


class CreateUserTemp(BaseModel):
    username: str
    phone_number: str


@router.post("/create-user", response_model=dict, status_code=status.HTTP_200_OK)
async def create_user(data: CreateUserTemp, database: Database = Depends(get_database)):

    new_user = User(
        id=ObjectId(),
        status=UserStatus.verified,
        username=data.username,
        phone_number=data.phone_number,
        joined_date=datetime.now(timezone.utc),
        is_agree_to_marketing_terms=True,
    )

    user_dict = new_user.model_dump(by_alias=True)

    user_id = await database.users.insert_one(user_dict)

    return {
        "user_id": str(user_id.inserted_id),
    }


@router.get("/user/{user_id}", response_model=UserResponse | None, status_code=status.HTTP_200_OK)
async def create_user(user_id: str, database: Database = Depends(get_database)):

    user_repo = UserRepository(database)

    doc = await user_repo.get_user_by_id(user_id)
    if not doc:
        return HTTPException(status_code=404, detail="NOT_FOUND")

    return UserResponse(**doc)
