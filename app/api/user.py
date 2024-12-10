from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Annotated

from app.core.database import db_conn

# from app.core.exceptions import NotFoundException
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


router = APIRouter()


@router.post("/add-new", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[Session, Depends(db_conn)]):
    try:
        # Create new user instance
        db_user = User(username=user.username, phone_number=user.phone_number, status=user.status)

        # Add to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    except IntegrityError as e:
        db.rollback()
        if "username" in str(e.orig):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
        elif "phone_number" in str(e.orig):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone number already exists")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Unique constraint violation")


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: int, db: Annotated[Session, Depends(db_conn)]):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            # status_code=status.HTTP_404_NOT_FOUND,
            status_code=200,
            detail=f"User with ID {user_id} not found",
        )

    return user
