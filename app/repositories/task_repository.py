from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate

class TaskRepository:


    def get_by_id(self,db: Session,task_id: int,owner_id: int):
        return db.scalar(
            select(Task).where(Task.id == task_id,
                Task.owner_id == owner_id,
            )
        )

    def get_all(self, db: Session, owner_id: int):
        return db.scalars(
            select(Task).where(Task.owner_id == owner_id)
        ).all()

    def create(
        self,
        db: Session,
        task_data: TaskCreate,
        owner_id: int,
    ) -> Task:

        new_task = Task(
        title=task_data.title,
        description=task_data.description,
        owner_id=owner_id,
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return new_task

    def update(
        self,
        db: Session,
        task: Task,
        title: str | None = None,
        description: str | None = None,
        completed: bool | None = None,
    ):
        if title is not None:
            task.title = title

        if description is not None:
            task.description = description

        if completed is not None:
            task.completed = completed

        db.commit()
        db.refresh(task)

        return task

    def delete(
        self,
        db: Session,
        task: Task,
    ):
        db.delete(task)
        db.commit()