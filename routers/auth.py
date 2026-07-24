import os
from datetime import datetime, timedelta, timezone
from typing import Annotated
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from models.users import UserModel
from schemas.auth import RefreshTokenSchema, Token, UserRegister
from core.limiter import limiter

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

if not SECRET_KEY:
  raise RuntimeError("Error: SECRET_KEY doesn`t have a value")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token/")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def truncate_to_72_bytes( password: str ) -> str:
  return password.encode("utf-8")[:72].decode("utf-8", errors="ignore")

def hash_password( password: str ) -> str:
  return pwd_context.hash(truncate_to_72_bytes(password))

def verify_password( plain_password: str, password: str ) -> bool:
  return pwd_context.verify(truncate_to_72_bytes(plain_password), password)


def create_jwt_token( data: dict, expires_delta: timedelta ) -> str:
  to_encode = data.copy()
  expire = datetime.now(timezone.utc) + expires_delta
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt

router = APIRouter()

@router.post("/token/", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request, db: Annotated[AsyncSession, Depends(get_db)], ):
  content_type = request.headers.get("content-type", "")

  if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
  else:
    try:
      json_data = await request.json()
      username = json_data.get("username")
      password = json_data.get("password")
    except Exception:
      raise HTTPException(status_code=400, detail="Invalid JSON payload")

  if not username or not password:
    raise HTTPException(
      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Username and password are required", )

  result = await db.execute(select(UserModel).where(UserModel.username == username))
  result = await db.execute(text(f"SELECT id, username, password FROM fastapi_users WHERE username = '{username}'"))
  user = result.scalar_one_or_none()
  if not user or not verify_password(password, user.password):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong username or password", )

  token_access = create_jwt_token(
    data={"sub": str(user.id), "type": "access"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), )

  token_refresh = create_jwt_token(
    data={"sub": str(user.id), "type": "refresh"}, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), )

  return {
    "access": token_access, "refresh": token_refresh, "access_token": token_access, "token_type": "bearer",
    }

# @router.post("/token/")
# async def break_login(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
#   json_data = await request.json()
#   username = json_data.get("username")
#   result = await db.execute(text(f"SELECT id, username, password FROM fastapi_users WHERE username = '{username}'"))
#   user = result.mappings().all()
#   return user


@router.post("/token/refresh/", response_model=Token)
async def refresh_token(
    payload: RefreshTokenSchema, db: Annotated[AsyncSession, Depends(get_db)], ):
  credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token", )
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
    data={"sub": str(user.id), "type": "access"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), )
  new_refresh = create_jwt_token(
    data={"sub": str(user.id), "type": "refresh"}, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), )

  return {
    "access": new_access, "refresh": new_refresh, "access_token": new_access, "token_type": "bearer",
    }


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)], ) -> UserModel:
  credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token expired or invalid", )
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
async def register(
    user_data: UserRegister, db: Annotated[AsyncSession, Depends(get_db)], ):
  username_check = await db.execute(
    select(UserModel).where(UserModel.username == user_data.username), )
  if username_check.scalar_one_or_none():
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists", )

  hashed_password = hash_password(user_data.password)

  new_user = UserModel(
    username=user_data.username, password=hashed_password, email="", first_name="", last_name="", is_superuser=False,
    is_staff=False, is_active=True, )
  db.add(new_user)
  await db.commit()
  await db.refresh(new_user)

  return {
    "message": "User created", "id": new_user.id, "username": new_user.username,
    }