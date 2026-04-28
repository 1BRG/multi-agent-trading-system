from pydantic import BaseModel


class ChatBase(BaseModel):
  title: str


class ChatRead(ChatBase):
  id: int
