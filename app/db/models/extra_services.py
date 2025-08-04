from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from app.db.base import Base

class ExtraServices(Base):
    __tablename__ = "extra_services"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[str] = mapped_column(nullable=True)
    title: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(nullable=False) 