from pydantic import BaseModel


class UserBase(BaseModel):
  email: str


class UserRead(UserBase):
  id: int
