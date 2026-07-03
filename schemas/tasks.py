from datetime import datetime
from typing import Annotated, Optional, Any

from pydantic import BaseModel, Field, field_validator, ConfigDict

PRIORITY_MAP = {
  "low": 1, "medium": 2, "high": 3
  }

REVERSED_PRIORITY_MAP = {
  1: "low", 2: "medium", 3: "high"
}

class TaskBase(BaseModel):

  title: str = Field(default ="New task")
  description: str = Field(default=None )
  priority: int = Field(default=1, ge=1, le= 3, description="Priority of task 1-5")

  @field_validator("title")
  @classmethod
  def validate_title( cls, value: str ) -> str:
    striped_value = value.strip()
    if not striped_value:
      raise ValueError("Title can`t be empty")
    return striped_value

  @field_validator("description")
  @classmethod
  def validate_desc(cls, value: str) -> str:
    strip_desc = value.strip()
    if not strip_desc:
      return strip_desc
    return value
class TaskCreate(TaskBase):
  title: str
  description: str | None = None
  priority: Any = Field(default="high")

  @field_validator("priority", mode="before")
  @classmethod
  def coerce_priority( cls, v: Any ) -> int:
    if isinstance(v, str):
      v_lower = v.strip().lower()
      if v_lower in PRIORITY_MAP:
        return PRIORITY_MAP[v_lower]
      if v.isdigit():
        return int(v)
    return 1

class TaskUpdate(TaskBase):
  title: Optional[str] = None
  description: Optional[str] = None
  completed: Optional[bool] = None
  priority: Optional[int] = Field(default=None)

  @field_validator("priority", mode="before")
  @classmethod
  def coerce_priority( cls, priority: Any ) -> Any:
    if isinstance(priority, str):
      priority_lower = priority.lower()
      if priority_lower in PRIORITY_MAP:
        return PRIORITY_MAP[priority_lower]
      if priority.isdigit():
        return int(priority)
    return priority

class TaskResponse(TaskBase):
  id: int
  title: str
  description: str
  completed: bool
  created_at: datetime
  owner_id: int
  priority: Any

  @field_validator("priority", mode="after")
  @classmethod
  def convert_to_str( cls , priority: int ) -> str:
    if isinstance(priority,int) and priority in REVERSED_PRIORITY_MAP:
      return REVERSED_PRIORITY_MAP[priority]
    return "low"
  model_config = ConfigDict(from_attributes=True)