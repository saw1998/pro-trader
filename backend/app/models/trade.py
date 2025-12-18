from decimal import Decimal
from sqlalchemy import UUID, DateTime, ForeignKey, Numeric, String, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
import uuid

from app.models.base import Base, TimestampMixin


class TradeSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class Trade(Base, TimestampMixin):
    '''Trade/transaction model'''
    
    __tablename__ = "trades"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    position_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("positions.id", ondelete="SET NULL"), nullable=True)
    symbol : Mapped[str] = mapped_column(String(20), nullable=False)
    side : Mapped[TradeSide] = mapped_column(SQLEnum(TradeSide), nullable=False)
    quantity : Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    price : Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    total_value : Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    fee : Mapped[Decimal] = mapped_column(Numeric(20,8),default=0)
    realized_pnl : Mapped[Decimal] = mapped_column(Numeric(20, 8), default=0)

    # Relationships


    __trade_args__ = (
        Index("idx_trades_user_created", "user_id", "created_at"),
        Index("idx_trades_symbol", "symbol")
    )

    def __repr__(self):
        return f"<Trade {self.side.value} {self.quantity} {self.symbol}@{self.price}"
        