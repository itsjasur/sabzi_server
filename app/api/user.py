from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.database import DB
from app.models.user import User
from app.schemas.user import UserResponse


router = APIRouter()


# @router.post("/add-new", status_code=status.HTTP_201_CREATED)
# async def create_user(user: UserCreate, db: Annotated[Session, Depends(db_conn)]):
#     try:
#         # create new user instance
#         db_user = User(username=user.username, phone_number=user.phone_number, status=user.status)

#         # add to database
#         db.add(db_user)
#         db.commit()
#         db.refresh(db_user)

#         return {"detail": "User added successfully"}

#     except IntegrityError as e:
#         if "username" in str(e.orig):
#             raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
#         elif "phone_number" in str(e.orig):
#             raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone number already exists")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Unique constraint violation")


@router.get("/my-info", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(db: DB):

    user = db.query(User).filter(User.id == 1).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user.id} not found",
        )

    return user
