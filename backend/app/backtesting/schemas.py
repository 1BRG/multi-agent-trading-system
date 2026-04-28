from pydantic import BaseModel


class BacktestRequest(BaseModel):
  strategy_id: int
  symbol: str


class BacktestPreview(BaseModel):
  status: str
