from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt
from pwdlib import PasswordHash

from src.schemas import Token
from src.settings import Settings

pwd_context = PasswordHash.recommended()


def get_password_hash(raw_password: str) -> str:
    return pwd_context.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(raw_password, hashed_password)


def create_token(
    which_token: Literal['access_token', 'refresh_token'], payload: dict = {}
) -> Token:
    to_encode = payload.copy()

    if which_token == 'access_token':
        key = Settings().ACCESS_TOKEN_KEY  # type:ignore
        expire = datetime.now(timezone(timedelta(hours=-3))) + timedelta(
            minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES  # type:ignore
        )

    elif which_token == 'refresh_token':
        key = Settings().REFRESH_TOKEN_KEY  # type:ignore
        expire = datetime.now(timezone(timedelta(hours=-3))) + timedelta(
            minutes=Settings().REFRESH_TOKEN_EXPIRE_MINUTES  # type:ignore
        )

    to_encode.update({'exp': expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, key, Settings().TOKEN_ALGORITHM)  # type:ignore

    return Token(token=encoded_jwt, token_type='Bearer')
