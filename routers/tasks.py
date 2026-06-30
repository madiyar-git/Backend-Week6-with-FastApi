from fastapi import APIRouter, status,HTTPException

router = APIRouter(
  prefix="/tasks"
  )

DB = {
  1: {"id":1, "title": "First task for test", "completed": False },
  2: {"id":2, "title": "Second task for test", "completed": True }
  }

@router.get("", status_code=status.HTTP_200_OK)
def get_tasks():
  return list(DB.values())

@router.get("/{task_id}", status_code=status.HTTP_200_OK)
def get_task(task_id: int):
  validation_task_id(task_id)

  return DB[task_id]

@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(task_data: dict):
  new_id = len(DB) + 1

  new_task = {
    "id": new_id,
    "title": task_data.get("title", "New task"),
    "completed": task_data.get("completed", False)
    }
  DB[new_id] = new_task
  return new_task

@router.put("/{task_id}", status_code=status.HTTP_200_OK)
def update_task(task_id: int, task_data: dict):
  validation_task_id(task_id)

  DB[task_id]["title"] = task_data.get("title", DB[task_id]["title"] )
  DB[task_id]["completed"] = task_data.get("completed", DB[task_id]["completed"])
  return DB[task_id]

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