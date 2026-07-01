import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
import bcrypt
from datetime import datetime, timedelta, timezone

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))

if not SECRET_KEY:
  raise RuntimeError("Error: SECRET_KEY doesn`t have value")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def hash_password(password:str) -> str:
  pwd_bytes = password.encode('utf-8')
  salt = bcrypt.gensalt()
  hashed = bcrypt.hashpw(pwd_bytes,salt)
  return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
  password_bytes = plain_password.encode('utf-8')
  hashed_bytes = hashed_password.encode('utf-8')
  return bcrypt.checkpw(password_bytes,hashed_bytes)



USERS_DB = {
  "User1": {
    "username": "User1", "hashed_password": hash_password("password123"), "email": "User1@example.com",
    }, "User2": {
    "username": "User2", "hashed_password": hash_password("password123"), "email": "User2@example.com",
    },
  }
class Token(BaseModel):
  access_token: str
  refresh_token: str
  token_type: str

router = APIRouter()

def create_access_token( data: dict ) -> str:
  to_encode = data.copy()
  expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt

@router.post("/login", response_model=Token)
def login( login_data: Annotated[ OAuth2PasswordRequestForm ,Depends()]):
  user = USERS_DB.get(login_data.username)
  if not user or not verify_password(login_data.password, user["hashed_password"]):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong username or password")
  access_token = create_access_token(data={"sub": user["username"]})
  return {"access_token": access_token, "token_type": "bearer", "refresh_token": "fake_refresh_token_for_now"}

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
  credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token expired")
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if username is None:
      raise credential_exception
  except JWTError:
    raise credential_exception
  user = USERS_DB.get(username)
  if user is None:
    raise credential_exception
  return user