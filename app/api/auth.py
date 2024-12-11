from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import DB
from app.core.utils.auth import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserLogin
from app.schemas.user import UserInfo


router = APIRouter()

# Simulate a database (replace with your actual database)
users_db = {}


# @router.post("/signup", response_model=dict)
# async def signup(user: UserCreate, db: DB):
#     if user.phone_numbeer in users_db:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

#     hashed_password = get_password_hash(user.password)
#     users_db[user.phone_numbeer] = {
#         "email": user.phone_numbeer,
#         "hashed_password": hashed_password,
#         "full_name": user.username,
#     }

#     return {
#         "message": "User created successfully",
#     }


@router.post("/send-code", response_model=Token)
async def login(user_credentials: UserLogin, db: DB):
    # user = users_db.get(user_credentials.phone_numbeer)
    user = db.query(User).filter(User.phone_number == UserLogin.phone_numbeer).first()

    if not user:
        # create new user instance
        db_user = User(username=user.username, phone_number=user.phone_number)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    if not verify_password(user_credentials.verification_code, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": user["email"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/verify-code", response_model=Token)
async def login(user_credentials: UserLogin, db: DB):
    pass
