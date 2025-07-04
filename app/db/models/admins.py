from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func, BigInteger, Boolean, text

from app.db.base import Base

from datetime import datetime


class Admins(Base):
    __tablename__ = "admins"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)
    telegram_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contractor: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(150), unique=False, nullable=False)
    hashed_psw: Mapped[str] = mapped_column(String(255), nullable=False)
    is_logged: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    role: Mapped[str] = mapped_column(String(10), default="admin", nullable=False)
    