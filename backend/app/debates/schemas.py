from pydantic import BaseModel


class DebateBase(BaseModel):
  topic: str


class DebateRead(DebateBase):
  id: int
