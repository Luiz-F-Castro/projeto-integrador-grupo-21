import uuid

from pydantic import BaseModel, Field

from app.models.enums import UserRole


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1)


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
