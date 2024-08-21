from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from src.dependencies import get_current_user, get_session
from src.models import LabelModel, UserModel
from src.schemas import (
    LabelCreateSchema,
    LabelPublicSchema,
    LabelsPublicSchema,
)

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


@router.get(
    '/all',
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=LabelsPublicSchema,
)
def show_all_labels(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    page_size: Annotated[int, Query(gt=0)] = 10,
    page: Annotated[int, Query(ge=0)] = 0,
    order_by: Annotated[
        str,
        Query(
            pattern=r'^(?:(?:id|title|color|priority|created_at)-'
            r'(?:asc|desc)){1}$'
        ),
    ] = 'priority-desc,',
):
    column, sort = order_by.split('-')

    orders = {
        'id': LabelModel.id,
        'title': LabelModel.title,
        'color': LabelModel.color,
        'priority': LabelModel.priority,
    }

    if sort == 'asc':
        order = asc(orders[column])

    else:
        order = desc(orders[column])

    labels = session.scalars(
        select(LabelModel)
        .where(LabelModel.user_id == current_user.id)
        .limit(page_size)
        .offset(page)
        .order_by(order)
    ).all()

    return {'labels': labels}


@router.get(
    '/{label_id}',
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=LabelPublicSchema,
)
def show_label(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    label_id: Annotated[int, Path()],
):
    label = session.scalar(
        select(LabelModel).where(
            LabelModel.user_id == current_user.id, LabelModel.id == label_id
        )
    )

    if label:
        return label

    raise HTTPException(
        detail='Label not found',
        status_code=status.HTTP_404_NOT_FOUND,
    )
