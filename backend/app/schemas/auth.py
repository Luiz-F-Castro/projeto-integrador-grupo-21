import uuid

from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserRead(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: UserRole
    account_locked: bool

    class Config:
        from_attributes = True