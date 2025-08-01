from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, func

from app.db.base import Base

from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.users import Users


class Invoice(Base):
    __tablename__ = "invoices"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    telegram_file_id: Mapped[str] = mapped_column(nullable=False)
    departure_city: Mapped[str] = mapped_column(nullable=False)
    recipient_city: Mapped[str] = mapped_column(nullable=False)
    invoice_number: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    user: Mapped["Users"] = relationship("Users", back_populates="invoices")