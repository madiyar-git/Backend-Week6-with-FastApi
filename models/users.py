from datetime import datetime

from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base


class UserModel(Base):
  __tablename__ = "auth_user"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  username: Mapped[str] = mapped_column(String,nullable=False )
  password: Mapped[str] = mapped_column("password",String, nullable=False)
  email: Mapped[str] = mapped_column(String, default="", nullable=False)
  first_name: Mapped[str] = mapped_column(String, default="", nullable=False)
  last_name: Mapped[str] = mapped_column(String, default="", nullable=False)
  is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
  is_staff: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
  is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
  date_joined: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

  tasks = relationship("TaskModel", back_populates="user_owner", cascade="all, delete-orphan")