from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.db import Base

class TaskTagModel(Base):
  __tablename__ = "fastapi_task_tags"

  id: Mapped[int] = mapped_column(primary_key=True)
  task_id: Mapped[int] = mapped_column(ForeignKey("fastapi_tasks.id", ondelete="CASCADE"))
  tag_id: Mapped[int] = mapped_column(ForeignKey("fastapi_tags.id", ondelete="CASCADE"))


class TagModel(Base):
  __tablename__ = "fastapi_tags"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(nullable=False)
  color: Mapped[str] = mapped_column(default="#1DB954")
  created_at: Mapped[datetime] = mapped_column(default=datetime.now)
  owner_id: Mapped[int] = mapped_column(ForeignKey("fastapi_users.id", ondelete="CASCADE"), nullable=False)

  tasks: Mapped[List["TaskModel"]] = relationship(
    "TaskModel", secondary=TaskTagModel.__table__, back_populates="tags"
    )

class TaskModel(Base):
  __tablename__ = "fastapi_tasks"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  title: Mapped[str] = mapped_column(nullable=False)
  description: Mapped[str] = mapped_column(default="", server_default="")
  completed: Mapped[bool] = mapped_column(default=False)
  priority: Mapped[int] = mapped_column(default=1)
  created_at: Mapped[datetime] = mapped_column(default=datetime.now)
  updated_at: Mapped[datetime] = mapped_column(
    default=datetime.now, onupdate=datetime.now, nullable=False
    )
  owner_id: Mapped[int] = mapped_column(ForeignKey("fastapi_users.id", ondelete="CASCADE"), nullable=False)

  tags = relationship(
    TagModel, secondary=TaskTagModel.__table__, back_populates="tasks"
    )
  user_owner = relationship("UserModel", back_populates="tasks")