from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from app.db.base import Base

class Tariffs(Base):
    __tablename__ = "tariffs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)