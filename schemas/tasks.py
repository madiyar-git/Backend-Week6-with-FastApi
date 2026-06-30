from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class TaskBase(BaseModel):
  title: str
  priority: int = Field(default=1, description="Priority of task 1-5")

class TaskCreate(TaskBase):

  @field_validator("title")
  @classmethod
  def validate_title( cls, value: str ) -> str: # todo нужно как то оптимизировать валдицию тайтла
    striped_value = value.strip()
    if not striped_value:
      raise ValueError("Title can`t be empty")
    return striped_value

  @field_validator("priority")
  @classmethod
  def validate_priority(cls, value: int) -> int:
    if 1 >= value >= 5:
      raise ValueError("Priority must be between 1 and 5")
    return value

class TaskUpdate(TaskBase):
  title: Optional[str] = None
  priority: Optional[int] = None
  completed: Optional[bool] = None

  @field_validator("title")
  @classmethod
  def validate_title(cls, value: Optional[str]) -> Optional[str]:
    if value is not None:
      stripped_value = value.strip()
      if not stripped_value:
        raise ValueError("Title can`t be empty")
      return stripped_value
    return value

  @field_validator("priority")
  @classmethod
  def validate_priority( cls, value: Optional[int] ) -> Optional[int]:
    if 1 >= value or value >= 5:
      raise ValueError("Priority must be between 1 and 5")
    return value


class TaskResponse(TaskBase):
  id: int
  title: str
  completed: bool
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)