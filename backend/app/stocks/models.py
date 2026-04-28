from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Stock(Base):
  __tablename__ = "stocks"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  symbol: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
  name: Mapped[str] = mapped_column(String(255), nullable=False)
