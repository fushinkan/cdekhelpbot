from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func, BigInteger, Boolean, text

from app.db.base import Base

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.invoices import Invoice
    from app.db.models.phone_numbers import PhoneNumbers


class Users(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)
    telegram_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    contract_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    city: Mapped[str] = mapped_column(String(32), nullable=False)
    contractor: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_psw: Mapped[str] = mapped_column(String(255), nullable=True)
    is_logged: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    role: Mapped[str] = mapped_column(String(10), default="user", nullable=False)
    
    access_token: Mapped[str] = mapped_column(nullable=True)
    refresh_token: Mapped[str] = mapped_column(nullable=True)
    
    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="user", cascade="all, delete-orphan")
    
    phones: Mapped[list["PhoneNumbers"]] = relationship(back_populates="user")