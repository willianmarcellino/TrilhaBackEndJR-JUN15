from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.settings import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login/')
engine = create_engine(Settings().DATABASE_URL)  # type:ignore


def get_session():
    with Session(engine, autoflush=False, autocommit=False) as session:
        yield session
