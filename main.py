import json
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler, middleware
from slowapi.errors import RateLimitExceeded
from core.limiter import limiter
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

@app.middleware("http")
async def extract_username(request: Request, call_next):
  if request.method == "POST" and request.url.path.endswith("/token/"):
    try:
      content_type = request.headers.get("content-type", "")
      if "application/json" in content_type:
        body = await request.body()
        if body:
          data = json.loads(body)
          request.state.username = data.get("username", "unknown")
      elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        request.state.username = form.get("username", "unknown")
    except Exception:
      request.state.username = "unknown"
  response = await call_next(request)
  return response

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router, prefix="/api", tags=["Auth"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
  CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=True,
  allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"] )

@app.get("/")
def root():
  return {"message": "FastAPI работает!"}
