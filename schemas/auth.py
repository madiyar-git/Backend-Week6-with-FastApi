from pydantic import BaseModel, model_validator, Field, field_validator


class LoginSchema(BaseModel):
  username: str = Field(min_length=3)
  password: str = Field(min_length=6)

  @field_validator('username', mode='before')
  @classmethod
  def spaces_remove( cls , username: str ):
    if isinstance(username, str):
      return username.strip()
    return username
class Token(BaseModel):
  access: str
  refresh: str
  access_token: str
  token_type: str = "bearer"

class RefreshTokenSchema(BaseModel):
  refresh: str

class UserRegister(LoginSchema):
  confirm_password: str = Field(min_length=6)

  @model_validator(mode="after")
  def check_match( self ):
    if self.password != self.confirm_password:
      raise ValueError("Password not match")
    return self