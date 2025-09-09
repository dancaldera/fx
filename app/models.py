from __future__ import annotations
from app import db
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
import enum

class TransactionType(enum.Enum):
    FUND = "fund"
    WITHDRAW = "withdraw"
    CONVERT_IN = "convert_in"
    CONVERT_OUT = "convert_out"

class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False, default=Decimal('0'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'currency', name='_user_currency_uc'),)
    
    def __repr__(self) -> str:
        return f'<Wallet {self.user_id}:{self.currency}={self.balance}>'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    from_currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    to_currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    fx_rate: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(20, 8), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<Transaction {self.id}: {self.user_id} {self.transaction_type.value} {self.amount} {self.currency}>'

class FxRate(db.Model):
    __tablename__ = 'fx_rates'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    to_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    rate: Mapped[Decimal] = mapped_column(DECIMAL(20, 8), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('from_currency', 'to_currency', name='_currency_pair_uc'),)
    
    def __repr__(self) -> str:
        return f'<FxRate {self.from_currency}/{self.to_currency}: {self.rate}>'