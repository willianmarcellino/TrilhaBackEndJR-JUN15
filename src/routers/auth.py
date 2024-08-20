from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.dependencies import get_session
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
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    user = session.scalar(
        select(UserModel).where(UserModel.username == form_data.username)
    )
    if user:
        if verify_password(form_data.password, user.password_hash):
            access_token = create_token('access_token', {'sub': user.username})

            return {'access_token': access_token}

    raise HTTPException(
        detail='Incorrect username or password',
        status_code=status.HTTP_400_BAD_REQUEST,
    )
