from typing import Optional
from pydantic import BaseModel, Field


class AuthSendCodeRequest(BaseModel):
    phone_number: str


class AuthVerifyCodeRequest(BaseModel):
    phone_number: str
    verification_code: str = Field(..., min_length=1, max_length=6)
    verification_token: str = Field(..., min_length=1, max_length=50)


class AuthVerifyCodeResponse(BaseModel):
    access_token: str
    is_new_user: Optional[bool] = False
