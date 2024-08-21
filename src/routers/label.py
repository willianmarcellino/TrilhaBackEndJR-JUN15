from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.dependencies import get_current_user, get_session
from src.models import LabelModel, UserModel
from src.schemas import LabelCreateSchema, LabelPublicSchema

router = APIRouter(prefix='/label', tags=['Label'])


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_class=JSONResponse,
    response_model=LabelPublicSchema,
)
def create_label(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    label_input: Annotated[LabelCreateSchema, Body()],
):
    current_datetime = datetime.now(timezone(timedelta(hours=-3)))
    label = LabelModel(
        title=label_input.title,
        color=label_input.color,
        priority=label_input.priority,
        updated_at=current_datetime,
        created_at=current_datetime,
        user_id=current_user.id,
    )

    try:
        session.add(label)
        session.commit()
        session.refresh(label)

    except Exception as error:  # pragma: no cover
        session.rollback()
        raise error

    return label
