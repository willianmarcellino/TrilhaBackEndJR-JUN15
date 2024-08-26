from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.models import UserModel
from src.settings import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login/')
engine = create_engine(Settings().DATABASE_URL)  # type:ignore


def get_session():
    with Session(engine, autoflush=False, autocommit=False) as session:
        yield session


def get_current_user(which_token: Literal['access_token', 'refresh_token']):
    def inner(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Annotated[Session, Depends(get_session)],
    ):
        credentials_exception = HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            'Invalid or expired token',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        try:
            if which_token == 'access_token':
                payload = jwt.decode(
                    jwt=token,
                    key=Settings().ACCESS_TOKEN_KEY,  # type:ignore
                    algorithms=[Settings().TOKEN_ALGORITHM],  # type:ignore
                    options={
                        'required': ['sub', 'exp'],
                        'verify_exp': False,
                    },
                )

            elif which_token == 'refresh_token':
                payload = jwt.decode(
                    jwt=token,
                    key=Settings().REFRESH_TOKEN_KEY,  # type:ignore
                    algorithms=[Settings().TOKEN_ALGORITHM],  # type:ignore
                    options={
                        'required': ['sub', 'exp'],
                        'verify_exp': False,
                    },
                )

            username = payload.get('sub')
            expire = payload.get('exp', 0)
            current_datetime = datetime.now(timezone(timedelta(hours=-3)))

            if expire > current_datetime.timestamp():
                user = session.scalar(
                    select(UserModel).where(UserModel.username == username)
                )

                if user:
                    return user

            raise credentials_exception

        except jwt.PyJWTError:
            raise credentials_exception

    return inner
