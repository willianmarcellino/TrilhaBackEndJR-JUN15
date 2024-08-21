import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.dependencies import get_current_user, get_session
from src.models import UserModel
from src.schemas import (
    UserCreateSchema,
    UserPublicSchema,
)
from src.security import get_password_hash

router = APIRouter(prefix='/user', tags=['User'])


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_class=JSONResponse,
    response_model=UserPublicSchema,
)
def create_user(
    user_input: Annotated[UserCreateSchema, Body()],
    session: Annotated[Session, Depends(get_session)],
):
    db_user = session.scalar(
        select(UserModel).where(
            or_(
                UserModel.email == user_input.email,
                UserModel.username == user_input.username,
            )
        )
    )

    if db_user:
        if user_input.username == db_user.username:
            raise HTTPException(
                detail='Username already exists',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        elif user_input.email == db_user.email:
            raise HTTPException(
                detail='Email already exists',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    current_datetime = datetime.now(timezone(timedelta(hours=-3)))
    user = UserModel(
        id=str(uuid.uuid4()),
        email=user_input.email,
        username=user_input.username,
        password_hash=get_password_hash(user_input.password),
        updated_at=current_datetime,
        created_at=current_datetime,
    )

    try:
        session.add(user)
        session.commit()

    except Exception as error:
        session.rollback()
        raise error

    return user


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=UserPublicSchema,
)
def show_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    return current_user
