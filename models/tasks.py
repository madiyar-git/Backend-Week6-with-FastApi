from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.db import Base

tasks_task_tags = Table(
    "tasks_task_tags",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("task_id", Integer, ForeignKey("tasks_task.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tasks_tag.id", ondelete="CASCADE")),
)


class TagModel(Base):
  __tablename__ = "tasks_tag"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  name: Mapped[str] = mapped_column(String, nullable=False)
  color: Mapped[str] = mapped_column(String, default="#1DB954")
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
  owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth_user.id", ondelete="CASCADE"), nullable=False)

  tasks: Mapped[List["TaskModel"]] = relationship(
    "TaskModel", secondary=tasks_task_tags, back_populates="tags"
    )

class TaskModel(Base):
  __tablename__ = "tasks_task"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True )
  title: Mapped[str] = mapped_column(String, nullable=False)
  description: Mapped[str] = mapped_column(String, default="", server_default="")
  completed:  Mapped[bool] = mapped_column(Boolean, default=False)
  priority: Mapped[int] = mapped_column(Integer, default=1)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
  updated_at: Mapped[datetime] = mapped_column(
    DateTime, default=datetime.now(),
    onupdate=datetime.now(),
    nullable=False
    )
  owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth_user.id", ondelete="CASCADE"), nullable=False)
  tags = relationship(
    TagModel, secondary=tasks_task_tags, back_populates="tasks")

  user_owner = relationship("UserModel", back_populates="tasks")