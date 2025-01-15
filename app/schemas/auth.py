# from typing import Optional
# from pydantic import BaseModel, Field, field_validator


# class AuthSendCodeRequest(BaseModel):
#     phone_number: str
#     is_agree_to_marketing_terms: Optional[bool] = False

#     @field_validator("phone_number")
#     def remove_spaces(cls, v):
#         return v.replace(" ", "")


# class AuthVerifyCodeRequest(BaseModel):
#     verification_code: str = Field(..., min_length=1)
#     verification_token: str = Field(..., min_length=1)
