from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Task, TaskStatus
from .schemas import TaskCreate


async def create_task(session: Session, task: TaskCreate) -> Task:
    db_task = Task(name=task.name, status=TaskStatus.PENDING)
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task


async def get_task(session: Session, task_id: int) -> Task:
    return await session.get(Task, task_id)


async def get_status(session: Session, task_date: str) -> dict[str, int]:
    result = await session.execute(
        select(Task.status, func.count(Task.id))
        .where(Task.create_time.like(f"%{task_date}%"))
        .group_by(Task.status)
    )
    return dict(result.all())


async def get_task_list(session: Session, task_date: str) -> list[Task]:
    result = await session.execute(
        select(Task).where(Task.create_time.like(f"%{task_date}%"))
    )
    return result.scalars().all()


async def update_task_status(
    session: Session, task: Task, status: TaskStatus, error_message=None, result=None
) -> Task:
    task.status = status
    if error_message:
        task.error_message = error_message
    if result:
        task.result = result
    task.end_time = datetime.now()
    await session.commit()
