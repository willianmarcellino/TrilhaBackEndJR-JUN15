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
from src.models import LabelModel, TaskModel, TaskStates, UserModel
from src.schemas import (
    InfoSuccessSchema,
    TaskCreateSchema,
    TaskPublicSchema,
    TasksPublicSchema,
    TaskUpdateSchema,
)

router = APIRouter(prefix='/task', tags=['Task'])


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_class=JSONResponse,
    response_model=TaskPublicSchema,
)
def create_task(
    current_user: Annotated[
        UserModel, Depends(get_current_user('access_token'))
    ],
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


@router.get(
    '/all',
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=TasksPublicSchema,
)
def show_all_tasks(
    current_user: Annotated[
        UserModel, Depends(get_current_user('access_token'))
    ],
    session: Annotated[Session, Depends(get_session)],
    page_size: Annotated[int, Query(gt=0)] = 10,
    page: Annotated[int, Query(ge=0)] = 0,
    order_by: Annotated[
        str,
        Query(
            pattern=r'^(?:(?:task_id|task_title|task_description|task_status|'
            r'task_expires_at|label_id|label_title|label_color|'
            r'label_priority)-(?:asc|desc)){1}$'
        ),
    ] = 'task_id-asc',
):
    orders = {
        'task_id': TaskModel.id,
        'task_title': TaskModel.title,
        'task_description': TaskModel.description,
        'task_status': TaskModel.status,
        'task_expires_at': TaskModel.expires_at,
        'label_id': LabelModel.id,
        'label_title': LabelModel.title,
        'label_color': LabelModel.color,
        'label_priority': LabelModel.priority,
    }

    column, sort = order_by.split('-')

    if sort == 'asc':
        order = asc(orders[column])

    elif sort == 'desc':
        order = desc(orders[column])

    if column[:4] == 'task':
        tasks = session.scalars(
            select(TaskModel)
            .where(TaskModel.user_id == current_user.id)
            .limit(page_size)
            .offset(page)
            .order_by(order)
        ).all()

    else:
        tasks = session.scalars(
            select(TaskModel)
            .join(LabelModel)
            .where(TaskModel.user_id == current_user.id)
            .limit(page_size)
            .offset(page)
            .order_by(order)
        ).all()

    for task in tasks:
        if (
            task.expires_at.timestamp()
            < datetime.now(timezone(timedelta(hours=-3))).timestamp()
        ):
            task.status = TaskStates.EXPIRED

    try:
        session.add(tasks)
        session.commit()
    except Exception as error:
        session.rollback()
        raise error

    return {'tasks': tasks}


@router.get(
    '/{task_id}',
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=TaskPublicSchema,
)
def show_task(
    current_user: Annotated[
        UserModel, Depends(get_current_user('access_token'))
    ],
    session: Annotated[Session, Depends(get_session)],
    task_id: Annotated[int, Path(gt=0)],
):
    task = session.scalar(
        select(TaskModel).where(
            TaskModel.user_id == current_user.id, TaskModel.id == task_id
        )
    )
    if task:
        if (
            task.expires_at.timestamp()
            < datetime.now(timezone(timedelta(hours=-3))).timestamp()
        ):
            task.status = TaskStates.EXPIRED

            try:
                session.add(task)
                session.commit()
            except Exception as error:
                session.rollback()
                raise error

        return task

    raise HTTPException(
        detail='Label not found', status_code=status.HTTP_404_NOT_FOUND
    )


@router.patch(
    '/{task_id}',
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=TaskPublicSchema,
)
def update_task(
    current_user: Annotated[
        UserModel, Depends(get_current_user('access_token'))
    ],
    session: Annotated[Session, Depends(get_session)],
    task_id: Annotated[int, Path()],
    task_input: Annotated[TaskUpdateSchema, Body()],
):
    task = session.scalar(
        select(TaskModel).where(
            TaskModel.user_id == current_user.id, TaskModel.id == task_id
        )
    )

    if task:
        if task_input.expires_at:
            if (
                task_input.expires_at.timestamp()
                < datetime.now(timezone(timedelta(hours=-3))).timestamp()
            ):
                return HTTPException(
                    detail='The datetime entered is in the past',
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            else:
                task.expires_at = task_input.expires_at

        if task_input.label_id:
            label_in_db = session.scalar(
                select(LabelModel).where(
                    LabelModel.user_id == current_user.id,
                    LabelModel.id == task_input.label_id,
                )
            )

            if not label_in_db:
                raise HTTPException(
                    detail='Label not found',
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            task.label_id = task_input.label_id

        for key, value in task_input.model_dump(exclude_unset=True).items():
            setattr(task, key, value)

        task.updated_at = datetime.now(timezone(timedelta(hours=-3)))

        try:
            session.add(task)
            session.commit()
            session.refresh(task)

        except Exception as error:
            session.rollback()
            raise error

        return task

    raise HTTPException(
        detail='Task not found', status_code=status.HTTP_404_NOT_FOUND
    )


@router.delete(
    '/{task_id}',
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=InfoSuccessSchema,
)
def delete_task(
    current_user: Annotated[
        UserModel, Depends(get_current_user('access_token'))
    ],
    session: Annotated[Session, Depends(get_session)],
    task_id: Annotated[int, Path()],
):
    task = session.scalar(
        select(TaskModel).where(
            TaskModel.user_id == current_user.id, TaskModel.id == task_id
        )
    )

    if task:
        try:
            session.delete(task)
            session.commit()

        except Exception as error:
            session.rollback()
            raise error

        return {'success': 'Task deleted successfully'}

    raise HTTPException(
        detail='Task not found', status_code=status.HTTP_404_NOT_FOUND
    )
