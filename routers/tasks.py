from datetime import datetime
from typing import List, Annotated
from fastapi import APIRouter, status, HTTPException, Depends
from schemas.tasks import TaskCreate, TaskUpdate, TaskResponse
from routers.auth import get_current_user

router = APIRouter()

DB = {
  1: {"id":1, "title": "First task for test", "completed": False, "priority": 3, "created_at": datetime.now(),
      "secret_db_field": "some_internal_telemetry_data", "owner": "User1" },
  2: {"id":2, "title": "Second task for test", "completed": True, "priority": 1, "created_at": datetime.now(),
      "secret_db_field": "some_internal_telemetry_data", "owner": "User2" }
  }


def get_task_or_404( task_id: int ) -> dict:
  if task_id not in DB:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id: {task_id} not found"
      )
  return DB[task_id]

@router.get("", response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def get_tasks(current_user: Annotated[dict, Depends(get_current_user)]):
  user_task = [task for task in DB.values() if task["owner"] == current_user["username"]]
  return user_task

@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task(task_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
  task = get_task_or_404(task_id)
  if task["owner"] != current_user["username"]:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don`t have task with this id ")
  return task

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate, current_user: Annotated[dict, Depends(get_current_user)]):
  new_id = max(DB.keys(), default=0) + 1
  new_task = {
    "id": new_id,
    "title": task_data.title,
    "completed": False,
    "priority": task_data.priority,
    "created_at": datetime.now(),
    "secret_db_field": "some_internal_telemetry_data",
    "owner": current_user["username"]
    }
  DB[new_id] = new_task
  return new_task

@router.put("/{task_id}", response_model=TaskUpdate, status_code=status.HTTP_200_OK)
def update_task(task_id: int, task_data: TaskUpdate, current_user: Annotated[dict, Depends(get_current_user)]):
  current_task = get_task_or_404(task_id)
  if current_task["owner"] != current_user["username"]:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don`t have task with this id ")
  if task_data.title is not None:
    current_task["title"] = task_data.title
  if task_data.priority is not None:
    current_task["priority"] = task_data.priority
  if task_data.completed is not None:
    current_task["completed"] = task_data.completed
  return current_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id:int, current_user: Annotated[dict, Depends(get_current_user)]):
  task = get_task_or_404(task_id)
  if task["owner"] != current_user["username"]:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don`t have task with this id ")
  del DB[task_id]