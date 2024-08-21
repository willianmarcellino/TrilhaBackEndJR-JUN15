from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    username: str
    email: str


class UserCreateSchema(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=255)]
    email: Annotated[EmailStr, Field(max_length=320)]
    password: Annotated[str, Field(min_length=8)]


class UserUpdateSchema(BaseModel):
    username: Annotated[str | None, Field(min_length=3, max_length=255)] = None
    email: Annotated[EmailStr | None, Field(max_length=320)] = None
    password: Annotated[str | None, Field(min_length=8)] = None


class Token(BaseModel):
    token: str
    token_type: str


class TokenSchema(BaseModel):
    access_token: Token
