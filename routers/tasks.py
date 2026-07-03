from typing import List, Annotated
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from models.users import UserModel
from schemas.tasks import TaskCreate, TaskUpdate, TaskResponse
from models.tasks import TaskModel
from routers.auth import get_current_user

router = APIRouter()


async def get_task_or_404( task_id: int, db: AsyncSession ) -> TaskModel:
  result = await db.execute(select(TaskModel).where(TaskModel.id == task_id))
  task = result.scalar_one_or_none()
  if not task:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id: {task_id} not found"
      )
  return task

@router.get("/", response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
async def get_tasks(current_user: Annotated[UserModel, Depends(get_current_user)],
  db: Annotated[AsyncSession, Depends(get_db)]):
  result = await db.execute(select(TaskModel).where(TaskModel.owner_id == current_user.id))
  return result.scalars().all()

@router.get("/{task_id}/", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def get_task(task_id: int, current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]):
  task = await get_task_or_404(task_id, db)
  if task.owner_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don`t have task with this id ")
  return task

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]):
  new_task = TaskModel(
    title = task_data.title,
    description = task_data.description,
    priority = task_data.priority,
    owner_id = current_user.id
  )
  db.add(new_task)
  await db.commit()
  await db.refresh(new_task)
  return new_task

@router.patch("/{task_id}/", response_model=TaskUpdate, status_code=status.HTTP_200_OK)
async def update_task(task_id: int, task_data: TaskUpdate,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]):
  current_task = await get_task_or_404(task_id, db)
  if current_task.owner_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don`t have task with this id ")
  if task_data.title is not None:
    current_task.title = task_data.title
  if task_data.description is not None:
    current_task.description = task_data.description
  if task_data.priority is not None:
    current_task.priority = task_data.priority
  if task_data.completed is not None:
    current_task.completed = task_data.completed
  await db.commit()
  await db.refresh(current_task)
  return current_task

@router.delete("/{task_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id:int, current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]):
  task = await get_task_or_404(task_id, db)
  if task.owner_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don`t have task with this id ")
  await db.delete(task)
  await db.commit()