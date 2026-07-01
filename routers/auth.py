from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(login: str, password: str):
  return {"message": "Login is valid"}

@router.post("/register")
def registration(login: str, password:str, confirm_pass: str):
  return {"message": "Registration done"}