from pydantic import BaseModel


class UserCreate(BaseModel):
    phone_numbeer: str
    verification_code: str
    username: str


class UserLogin(BaseModel):
    phone_numbeer: str
    verification_code: str


class Token(BaseModel):
    access_token: str
    token_type: str
