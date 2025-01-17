from datetime import datetime, timedelta, timezone
import random
import secrets
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.database import Database, get_database
from app.core.utils.sms import send_sms
from app.models.user import UserStatus, Verification
from app.models.auth import *
from app.repositories.user import *
from app.schemas.auth import *


router = APIRouter()


@router.post("/check-new-user", response_model=dict)
async def check_new_user(
    data: AuthWithPhoneNumber,
    database: Database = Depends(get_database),
    user_repo: UserRepository = Depends(UserRepository),
):

    user = await user_repo.get_user_by_phone_number(data.phone_number)

    if not user:
        return {"is_new_user": True}

    return {"is_new_user": False}


@router.post("/request-code", response_model=dict)
async def send_code(
    data: AuthWithPhoneNumber,
    database: Database = Depends(get_database),
    verification_repo: VerificationRepository = Depends(VerificationRepository),
):

    # checks if user requested too many times
    limit_reached: bool = await verification_repo.check_verification_limit(data.phone_number)
    if limit_reached:
        raise HTTPException(status_code=400, detail="TOO_MANY_ATTEMPTS")

    # generates new verification
    verification_code = 111111  # random.randint(100000, 999999)

    verification = Verification(
        phone_number=data.phone_number,
        code=verification_code,
        attempts=5,
        created_date=datetime.now(timezone.utc),
    )
    result = await database.verifications.insert_one(verification.model_dump(by_alias=True))
    verification_id = result.inserted_id

    # sends SMS with the verification code
    await send_sms(data.phone_number, verification_code)

    return {
        "detail": "CODE_SENT",
        "verification_id": str(verification_id),
    }


@router.post("/verify-code", response_model=AuthVerifyCodeResponse)
async def verify_code(
    data: AuthVerifyCodeRequest,
    verification_repo: VerificationRepository = Depends(VerificationRepository),
    user_repo: UserRepository = Depends(UserRepository),
):

    verification: Verification = await verification_repo.get_verification_by_id(data.verification_id)

    await verification_repo.decrement_attempts(verification.id)

    # checks if user is available
    user: User | None = await user_repo.get_user_by_phone_number(verification.phone_number)
    user_id = user.id if user else None

    if verification.attempts == 0 or verification.created_date + timedelta(minutes=5) < datetime.now(timezone.utc):
        raise HTTPException(status_code=404, detail="INVALID_OR_EXPIRED_TOKEN")

    # verification failed attempt
    if verification.code != data.verification_code:
        raise HTTPException(status_code=404, detail=f"FAILED_ATTEMPT_{verification.attempts}")

    # verification token should be secure
    verification_token = secrets.token_hex(32)

    verification.user_id = user_id
    verification.token = verification_token
    verification.attempts = 0

    # update verification
    await verification_repo.update_verification(verification)

    # if not new user
    unique_usernames = []
    if user:
        # get random usernames from the db
        result = await verification_repo.get_random_usernames()
        unique_usernames = {user["username"] for user in result}
        if len(unique_usernames) < 10:
            unique_usernames = unique_usernames | {"Javlik", "Oltin", "ali", "Сардор", "patriot", "bravo", "Алексей"}

        # limits count to 10
        unique_usernames = list(unique_usernames)[:10]

        # adds real username and then shuffles
        unique_usernames.append(user.username)
        random.shuffle(unique_usernames)

    return AuthVerifyCodeResponse(
        success=True,
        verification_token=verification_token,
        is_new_user=True,
        random_usernames=unique_usernames,
    )


@router.post("/verify-username", response_model=dict)
async def verify_username(
    data: AuthVerifyUsernameRequest,
    database: Database = Depends(get_database),
    verification_repo: VerificationRepository = Depends(VerificationRepository),
    user_repo: UserRepository = Depends(UserRepository),
):

    verification: Verification = await verification_repo.get_verification_by_token(data.verification_token)
