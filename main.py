from fastapi import FastAPI
from routers.tasks import router as tasks_router
from routers.auth import router as auth_router

app = FastAPI()

app.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

@app.get("/")
def root():
  return {"message": "FastAPI работает!"}