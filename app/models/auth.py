from pydantic import BaseModel, Field, field_validator


class AuthWithPhoneNumber(BaseModel):
    phone_number: str = Field(..., min_length=1)

    @field_validator("phone_number")
    def remove_spaces(cls, v):
        return v.replace(" ", "")


class AuthVerifyCodeRequest(BaseModel):
    verification_code: int
    verification_id: str = Field(..., min_length=1)


class AuthVerifyUsernameRequest(BaseModel):
    verification_token: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)


class AuthVerifyCodeResponse(BaseModel):
    success: bool
    verification_token: str
    is_new_user: bool
    random_usernames: list[str]
