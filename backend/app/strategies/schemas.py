from pydantic import BaseModel


class StrategyBase(BaseModel):
  name: str


class StrategyRead(StrategyBase):
  id: int
