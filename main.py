import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.db import Base, engine
from routers.auth import router as auth_router
from routers.tasks import router as tasks_router

load_dotenv(override=True)


@asynccontextmanager
async def lifespan( app: FastAPI ):
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/api", tags=["Auth"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
  CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=True,
  allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"], )

@app.get("/")
def root():
  return {"message": "FastAPI работает!"}
