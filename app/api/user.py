from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.database import DB
from app.core.utils.auth import AUTH_ME
from app.models.user import User
from app.schemas.user import UserResponse


router = APIRouter()


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(user: AUTH_ME):
    return user
