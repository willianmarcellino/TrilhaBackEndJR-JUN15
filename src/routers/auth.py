from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.dependencies import get_current_user, get_session
from src.models import UserModel
from src.schemas import TokenSchema
from src.security import create_token, verify_password

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post(
    '/login',
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=TokenSchema,
)
def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: Annotated[Session, Depends(get_session)],
):
    user = session.scalar(
        select(UserModel).where(UserModel.username == username)
    )

    if user:
        if verify_password(password, user.password_hash):
            access_token = create_token('access_token', {'sub': user.username})
            return {'access_token': access_token}

    raise HTTPException(
        detail='Incorrect username or password',
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@router.post(
    '/refresh-token',
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=TokenSchema,
)
def refresh_token(
    current_user: Annotated[
        UserModel, Depends(get_current_user('refresh_token'))
    ],
):
    access_token = create_token('access_token', {'sub': current_user.username})
    refresh_token = create_token(
        'refresh_token', {'sub': current_user.username}
    )

    return {'access_token': access_token, 'refresh_token': refresh_token}
