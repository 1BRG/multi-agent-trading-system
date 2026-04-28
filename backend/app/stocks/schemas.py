from pydantic import BaseModel


class StockBase(BaseModel):
  symbol: str
  name: str


class StockRead(StockBase):
  id: int
