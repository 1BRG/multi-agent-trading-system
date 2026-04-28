from pydantic import BaseModel


class BacktestBase(BaseModel):
  status: str


class BacktestRead(BacktestBase):
  id: int
