from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class TaskBase(BaseModel):
  title: str
  priority: int = Field(default=1, ge=1, le= 5, description="Priority of task 1-5")
  @field_validator("title")
  @classmethod
  def validate_title( cls, value: str ) -> str:
    striped_value = value.strip()
    if not striped_value:
      raise ValueError("Title can`t be empty")
    return striped_value
class TaskCreate(TaskBase):
  pass

class TaskUpdate(TaskBase):
  title: Optional[str] = None
  priority: Optional[int] = None
  completed: Optional[bool] = None

class TaskResponse(TaskBase):
  id: int
  title: str
  completed: bool
  created_at: datetime
  owner: str

  model_config = ConfigDict(from_attributes=True)