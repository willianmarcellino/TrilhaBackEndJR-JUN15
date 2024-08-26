from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.models import TaskStates


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


class InfoSuccessSchema(BaseModel):
    success: str


class LabelPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    color: str
    priority: int
    updated_at: datetime
    created_at: datetime


class LabelsPublicSchema(BaseModel):
    labels: list[LabelPublicSchema]


class LabelCreateSchema(BaseModel):
    title: Annotated[str, Field(max_length=100)]
    color: Annotated[
        str,
        Field(min_length=7, max_length=7, pattern=r'^#[0-9a-fA-F]{6}$'),
    ]
    priority: Annotated[int, Field(ge=1, le=10)]


class LabelUpdateSchema(BaseModel):
    title: Annotated[str | None, Field(max_length=100)] = None
    color: Annotated[str | None, Field(pattern=r'^#[0-9a-fA-F]{6}$')] = None
    priority: Annotated[int | None, Field(ge=1, le=10)] = None


class TaskPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    status: TaskStates
    label: LabelPublicSchema | None = None
    expires_at: datetime
    updated_at: datetime
    created_at: datetime


class TasksPublicSchema(BaseModel):
    tasks: list[TaskPublicSchema]


class TaskCreateSchema(BaseModel):
    title: Annotated[str, Field(max_length=100)]
    description: Annotated[str, Field(max_length=255)] = ''
    expires_at: Annotated[datetime, Field()]
    label_id: Annotated[int | None, Field(gt=0)] = None


class TaskUpdateSchema(BaseModel):
    title: Annotated[str | None, Field(max_length=100)] = None
    status: TaskStates | None = None
    description: Annotated[str | None, Field(max_length=255)] = None
    expires_at: Annotated[datetime | None, Field()] = None
    label_id: Annotated[int | None, Field(gt=0)] = None
