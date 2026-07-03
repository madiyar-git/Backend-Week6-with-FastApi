import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from schemas.auth import LoginSchema, RefreshTokenSchema, UserRegister, Token

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from models.users import UserModel

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

if not SECRET_KEY:
  raise RuntimeError("Error: SECRET_KEY doesn`t have value")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token/")

pwd_context = CryptContext(
    schemes=["bcrypt", "django_pbkdf2_sha256"],
    deprecated="auto"
)

def hash_password(password:str) -> str:
  return pwd_context.hash(password)

def verify_password(plain_password: str, password: str) -> bool:
  return pwd_context.verify(plain_password,password)

router = APIRouter()

def create_jwt_token( data: dict, expires_delta: timedelta ) -> str:
  to_encode = data.copy()
  expire = datetime.now(timezone.utc) + expires_delta
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt

@router.post("/token/", response_model=Token)
async def login( login_data: LoginSchema,
    db: Annotated[AsyncSession, Depends(get_db)]):

  result = await db.execute(select(UserModel).where(UserModel.username == login_data.username))
  user = result.scalar_one_or_none()

  if not user or not verify_password(login_data.password, user.password):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong username or password")

  access_token = create_jwt_token(data={"sub": str(user.id), "type": "access"},
    expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

  refresh_token = create_jwt_token(data={"sub": str(user.id), "type": "refresh"},
    expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
  return {
    "access": access_token, "refresh": refresh_token
    }

@router.post("/token/refresh/", response_model= Token)
async def refresh_token(payload: RefreshTokenSchema,db:Annotated[AsyncSession, Depends(get_db)]):
  credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
    )
  try:
    decode_payload = jwt.decode(payload.refresh, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = decode_payload.get("sub")
    token_type: str = decode_payload.get("type")
    if user_id is None or token_type != "refresh":
      raise credential_exception
  except JWTError:
    raise credential_exception

  result = await db.execute(select(UserModel).where(UserModel.id == int(user_id)))
  user = result.scalar_one_or_none()
  if user is None:
    raise credential_exception
  new_access = create_jwt_token(
    data={"sub": str(user.id), "type": "access"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) )
  new_refresh = create_jwt_token(
    data={"sub": str(user.id), "type": "refresh"}, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS) )

  return {"access": new_access, "refresh": new_refresh}

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]) -> UserModel:
  credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token expired")
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")
    if user_id is None or token_type != "access":
      raise credential_exception
  except JWTError:
    raise credential_exception

  result = await db.execute(select(UserModel).where(UserModel.id == int(user_id)))
  user = result.scalar_one_or_none()
  if user is None:
    raise credential_exception
  return user

@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Annotated[AsyncSession, Depends(get_db)]):
  username_check = await db.execute(select(UserModel).where(UserModel.username == user_data.username))
  if username_check.scalar_one_or_none():
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already existing ")


  hashed_password = pwd_context.hash(user_data.password, scheme="django_pbkdf2_sha256")

  new_user = UserModel(
    username=user_data.username,
    password=hashed_password,
    email="",
    first_name="",
    last_name="",
    is_superuser=False,
    is_staff=False,
    is_active=True
    )
  db.add(new_user)
  await db.commit()
  await db.refresh(new_user)

  return {
    "message": "User created",
    "id": new_user.id,
    "username": new_user.username
    }