from datetime import datetime
from typing import List
from fastapi import APIRouter, status,HTTPException
from schemas.tasks import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(
  prefix="/tasks",
  tags=["Tasks"]
  )

DB = {
  1: {"id":1, "title": "First task for test", "completed": False, "priority": 3, "created_at": datetime.now(), "secret_db_field": "some_internal_telemetry_data" },
  2: {"id":2, "title": "Second task for test", "completed": True, "priority": 1, "created_at": datetime.now(), "secret_db_field": "some_internal_telemetry_data" }
  }

@router.get("", response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def get_tasks():
  return list(DB.values())

@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task(task_id: int):
  validation_task_id(task_id)

  return DB[task_id]

@router.post("", response_model=TaskCreate, status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate):
  new_id = len(DB) + 1

  new_task = {
    "id": new_id,
    "title": task_data.title,
    "completed": False,
    "priority": task_data.priority,
    "created_at": datetime.now(),
    "secret_db_field": "some_internal_telemetry_data"
    }
  DB[new_id] = new_task
  return new_task

@router.put("/{task_id}", response_model=TaskUpdate, status_code=status.HTTP_200_OK)
def update_task(task_id: int, task_data: TaskUpdate):
  validation_task_id(task_id)

  current_task = DB[task_id]
  if task_data.title is not None:
    current_task["title"] = task_data.title
  if task_data.priority is not None:
    current_task["priority"] = task_data.priority
  if task_data.completed is not None:
    current_task["completed"] = task_data.completed
  return current_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id:int):
  validation_task_id(task_id)
  del DB[task_id]

def validation_task_id(task_id: int):
  if task_id not in DB:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Task with id: {task_id} not found"
      )
  return task_id