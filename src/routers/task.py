from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.dependencies import get_current_user, get_session
from src.models import LabelModel, TaskModel, TaskStates, UserModel
from src.schemas import TaskCreateSchema, TaskPublicSchema

router = APIRouter(prefix='/task', tags=['Task'])


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_class=JSONResponse,
    response_model=TaskPublicSchema,
)
def create_task(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    task_input: Annotated[TaskCreateSchema, Body()],
):
    current_datetime = datetime.now(timezone.utc) - timedelta(hours=3)

    if task_input.expires_at < current_datetime:
        raise HTTPException(
            detail='Expires_at is in the past',
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    task = TaskModel(
        title=task_input.title,
        description=task_input.description,
        status=TaskStates.PENDING,
        expires_at=task_input.expires_at,
        user_id=current_user.id,
    )

    if task_input.label_id:
        label = session.scalar(
            select(LabelModel).where(
                LabelModel.user_id == current_user.id,
                LabelModel.id == task_input.label_id,
            )
        )

        if label:
            task.label_id = label.id
        else:
            raise HTTPException(
                detail='Label not found',
                status_code=status.HTTP_404_NOT_FOUND,
            )

    current_datetime = datetime.now(timezone(timedelta(hours=-3)))
    task.updated_at = current_datetime
    task.created_at = current_datetime

    try:
        session.add(task)
        session.commit()
        session.refresh(task)

    except Exception as error:  # pragma: no cover
        session.rollback()
        raise error

    return task
