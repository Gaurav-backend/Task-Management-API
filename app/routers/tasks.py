import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

from app.core.security import get_current_active_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


task_repository = TaskRepository()



@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        created_task = task_repository.create(
            db=db,
            task_data=task,
            owner_id=current_user.id,
        )

        logger.info(
            "Task created successfully task_id=%s owner_id=%s",
            created_task.id,
            current_user.id,
        )

        return created_task

    except Exception:
        logger.exception(
            "Task creation failed owner_id=%s",
            current_user.id,
        )
        raise



@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return task_repository.get_all(
        db=db,
        owner_id=current_user.id,
    )




@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    task = task_repository.get_by_id(
        db=db,
        task_id=task_id,
        owner_id=current_user.id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task




@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    task = task_repository.get_by_id(
        db=db,
        task_id=task_id,
        owner_id=current_user.id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    updated_task = task_repository.update(
        db=db,
        task=task,
        title=task_update.title,
        description=task_update.description,
        completed=task_update.completed,
    )

    return updated_task




@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    task = task_repository.get_by_id(
        db=db,
        task_id=task_id,
        owner_id=current_user.id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    task_repository.delete(db, task)