from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Chat(Base):
  __tablename__ = "chats"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  title: Mapped[str] = mapped_column(String(255), nullable=False)
