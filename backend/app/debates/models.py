from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Debate(Base):
  __tablename__ = "debates"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  topic: Mapped[str] = mapped_column(String(255), nullable=False)
