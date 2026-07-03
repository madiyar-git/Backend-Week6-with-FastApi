from pydantic import BaseModel, model_validator


class LoginSchema(BaseModel):
  username: str
  password: str

class Token(BaseModel):
  access: str
  refresh: str

class RefreshTokenSchema(BaseModel):
  refresh: str

class UserRegister(BaseModel):
  username: str
  password: str
  confirm_password: str

  @model_validator(mode="after")
  def check_match( self ):
    if self.password != self.confirm_password:
      raise ValueError("Password not match")
    return self