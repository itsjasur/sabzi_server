from datetime import datetime, timezone
import random
import secrets
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.core.database import DB
from app.core.utils.auth import create_access_token
from app.core.utils.sms import send_sms
from app.models.user import User, UserStatus, UserVerification
from app.schemas.auth import AuthSendCodeRequest, AuthVerifyCodeRequest, AuthVerifyCodeResponse


router = APIRouter()


@router.post("/send-code", response_model=dict)
def login(data: AuthSendCodeRequest, db: DB):
    # when querying by primary key (ID)
    # user = db.get(User, 123)

    #  check if user exists
    stmt = select(User).where(User.phone_number == data.phone_number)  # querying by non-primary key fields
    user = db.execute(stmt).scalar()

    #  check if user doesn't exist add new user
    if not user:
        user = User(phone_number=data.phone_number)
        db.add(user)
        db.commit()
        db.refresh(user)

    stmt = select(UserVerification).where(
        UserVerification.user_id == user.id,
        UserVerification.phone_number == data.phone_number,
        UserVerification.expires_at > datetime.now(timezone.utc),
    )

    verification: UserVerification | None = db.execute(stmt).scalar()

    # verification token to prevent brute attack phone number checks (session identifier)
    verification_token: str = secrets.token_urlsafe(32)

    if not verification:
        verification = UserVerification(
            user_id=user.id,
            phone_number=data.phone_number,
            verification_code=str(random.randint(100000, 999999)),
            verification_token=verification_token,
        )
        db.add(verification)
        db.commit()
        db.refresh(verification)

    # send SMS here to user phone number
    send_sms(data.phone_number)

    return {
        "details": "Verification code is sent. Plese check SMS history",
        "verification_token": verification_token,
        "tem_code": verification.verification_code,
    }


@router.post("/verify-code", response_model=AuthVerifyCodeResponse)
def verify_code(data: AuthVerifyCodeRequest, db: DB):

    stmt = select(UserVerification).where(
        UserVerification.verification_token == data.verification_token,
        UserVerification.attempts > 0,
        UserVerification.expires_at > datetime.now(timezone.utc),
    )
    verification: UserVerification | None = db.execute(stmt).scalar()

    if not verification:
        raise HTTPException(status_code=400, detail="Invalid verification request")

    # checks the code
    if verification.verification_code != data.verification_code:
        verification.attempts -= 1
        db.commit()
        raise HTTPException(status_code=400, detail=f"Invalid code. {verification.attempts} attempts remaining")

    # update user status to active
    user = db.get(User, verification.user_id)
    if user:
        user.status = UserStatus.verified
        db.commit()

    access_token: str = create_access_token({"user_id": verification.user_id})

    return AuthVerifyCodeResponse(access_token=access_token, is_new_user=True)
