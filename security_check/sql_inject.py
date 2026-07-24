from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from models.users import UserModel

router = APIRouter()

class UserSchema(BaseModel):
  username: str

# router.post("/")
# async def sql_check(data: UserSchema, db: Annotated[AsyncSession, Depends(get_db)]):
#   query = text(f"SELECT id, username FROM fastapi_users WHERE username = '{data.username}'")
#
#   result = await db.execute(query)
#   rows = result.mappings().all()
#   return {"result": rows}

# @router.post("/")
# async def sql_check(data: UserSchema, db: Annotated[AsyncSession, Depends(get_db)]):
#   query = text("SELECT id, username FROM fastapi_users WHERE username = :username")
#
#   result = await db.execute(query, {"username": data.username})
#   rows = result.mappings().all()
#   return {"result": rows}

@router.post("/")
async def sql_check(data: UserSchema, db: Annotated[AsyncSession, Depends(get_db)]):
  res = await db.execute(select(UserModel.id, UserModel.username).where(UserModel.username == data.username))
  rows = res.mappings().all()
  return {"result": rows}