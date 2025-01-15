# from datetime import datetime, timedelta, timezone
# import random
# import secrets
# from fastapi import APIRouter, HTTPException
# from sqlalchemy import select
# from app.core.database import DB
# from app.core.utils.auth import create_access_token
# from app.core.utils.sms import send_sms
# from app.models.user import User, UserStatus, UserVerification
# from app.schemas.auth import *


# router = APIRouter()


# @router.post("/check-new-user", response_model=dict)
# def check_new_user(data: AuthSendCodeRequest, db: DB):

#     stmt = select(User).where(User.phone_number == data.phone_number)
#     user = db.execute(stmt).scalar()

#     if not user:
#         return {"is_new_user": True}

#     return {"is_new_user": False}


# @router.post("/send-code", response_model=dict)
# def send_code(data: AuthSendCodeRequest, db: DB):
#     print(data.model_dump())

#     # check if user exists
#     stmt = select(User).where(User.phone_number == data.phone_number)
#     user = db.execute(stmt).scalar()

#     # check if user doesn't exist add new user
#     if not user:
#         user = User(
#             phone_number=data.phone_number,
#             is_agree_to_marketing_terms=data.is_agree_to_marketing_terms,
#         )
#         db.add(user)
#         db.commit()
#         db.refresh(user)

#     # Generate new verification
#     verification_token = secrets.token_urlsafe(32)
#     # verification_code = str(random.randint(100000, 999999))
#     verification_code = str(111111)
#     verification = UserVerification(
#         user_id=user.id,
#         phone_number=data.phone_number,
#         verification_code=verification_code,
#         verification_token=verification_token,
#     )
#     db.add(verification)
#     db.commit()
#     db.refresh(verification)

#     # Send SMS with the verification code (whether new or existing)
#     send_sms(data.phone_number, verification_code)

#     return {
#         "details": "Verification code is sent. Please check SMS history",
#         "verification_token": verification_token,
#         "tem_code": verification.verification_code,
#     }


# @router.post("/verify-code", response_model=dict)
# def verify_code(data: AuthVerifyCodeRequest, db: DB):
#     print(data.model_dump())

#     # Include expiration check in initial query
#     stmt = (
#         select(UserVerification)
#         .where(
#             UserVerification.verification_token == data.verification_token,
#             UserVerification.attempts > 0,
#             UserVerification.expires_at > datetime.now(timezone.utc),
#         )
#         .with_for_update()
#     )

#     verification: UserVerification | None = db.execute(stmt).scalar()

#     if not verification:
#         raise HTTPException(status_code=404, detail="INVALID_OR_EXPIRED_TOKEN")

#     verification.attempts -= 1
#     db.commit()

#     # reject immediately
#     if verification.attempts == 0:
#         raise HTTPException(status_code=404, detail="INVALID_OR_EXPIRED_TOKEN")

#     # checks the code
#     if verification.verification_code != data.verification_code:
#         raise HTTPException(
#             status_code=400,
#             detail=f"INVALID_CODE_ATTEMPTS_{verification.attempts}",
#         )

#     user = db.get(User, verification.user_id)
#     if not user:
#         raise HTTPException(status_code=400, detail="USER_NOT_FOUND")

#     # successful verification
#     user.status = UserStatus.verified
#     verification.attempts = 0
#     db.commit()

#     access_token: str = create_access_token({"user_id": verification.user_id})

#     return {"access_token": access_token}
