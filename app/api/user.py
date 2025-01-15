from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import DB
from app.models.user import UserCreate, UserStatus
from app.repositories.user import UserRepository


router = APIRouter()


@router.get("/create-user", response_model=dict, status_code=status.HTTP_200_OK)
async def create_user(user_repo: UserRepository = Depends(UserRepository)):

    new_user = UserCreate(
        status=UserStatus.unverified,
        username="jasur",
        joined_date=datetime.now(timezone.utc),
    )

    user_id = await user_repo.create_user(new_user)

    return {
        "user_id": str(user_id),
    }


@router.get("/user/{user_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def create_user(user_id: str, user_repo: UserRepository = Depends(UserRepository)):

    user = await user_repo.get_user_by_id(user_id)

    return {
        "user_info": user,
    }


@router.post("/users", response_model=dict, status_code=status.HTTP_200_OK)
async def get_users(user_repo: UserRepository = Depends(UserRepository)):

    users = await user_repo.get_users()
    return {"users": users}
