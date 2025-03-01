from pydantic import BaseModel, Field
from typing import Optional
import datetime


class Token(BaseModel):
    access_token: str = Field(..., description="The access token")
    token_type: str = Field(..., description="The token type")


class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="The username of the user")


class UserCreate(BaseModel):
    username: str = Field(..., max_length=50, description="The username of the user")
    full_name: str = Field(..., max_length=255, description="The full name of the user")
    hashed_password: str = Field(..., description="The hashed password of the user")
    is_superuser: bool = Field(False, description="The role of the user")


class UserUpdate(UserCreate):
    username: Optional[str] = Field(None, max_length=50, description="The username of the user")
    full_name: Optional[str] = Field(None, max_length=255, description="The full name of the user")
    hashed_password: Optional[str] = Field(None, description="The hashed password of the user")


class UserRead(UserCreate):
    id: int = Field(..., description="The ID of the user")
    disabled: bool = Field(..., description="The status of the user")
    is_superuser: bool = Field(..., description="The role of the user")
    full_name: str = Field(..., description="The full name of the user")
    created_at: datetime.datetime = Field(..., description="The time the user was created")
    updated_at: datetime.datetime = Field(..., description="The time the user was updated")


class UserResponse(BaseModel):
    id: int = Field(..., description="The ID of the user")
    username: str = Field(..., description="The username of the user")
    full_name: str = Field(..., description="The full name of the user")
    is_superuser: bool = Field(..., description="The role of the user")