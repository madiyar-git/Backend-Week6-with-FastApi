from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.db import engine, Base
from routers.tasks import router as tasks_router
from routers.auth import router as auth_router


@asynccontextmanager
async def lifespan( app: FastAPI ):
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/api")
app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])

@app.get("/")
def root():
  return {"message": "FastAPI работает!"}