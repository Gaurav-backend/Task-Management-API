from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task


class TaskRepository:

    def get_by_id(self, db: Session, task_id: int):
        return db.scalar(
            select(Task).where(Task.id == task_id)
        )

    def get_all(self, db: Session):
        return db.scalars(
            select(Task)
        ).all()

    def create(self, db: Session, title: str, description: str | None):
        new_task = Task(
            title=title,
            description=description,
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

    def delete(self, db: Session, task: Task):
        db.delete(task)
        db.commit()