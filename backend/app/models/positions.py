from datetime import datetime
from decimal import Decimal
from sqlalchemy import UUID, DateTime, ForeignKey, Numeric, String, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
import uuid

from app.models.base import Base, TimestampMixin


class PositionType(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class PositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    # PARTIAL = "PARTIAL"

class Position(Base, TimestampMixin):
    '''Position model'''

    __tablename__ = "positions"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id : Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    symbol : Mapped[str] = mapped_column(String(20), nullable=False)
    entry_price : Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)
    quantity : Mapped[float] = mapped_column(Numeric(20,8), nullable=False)
    position_type : Mapped[PositionType] = mapped_column(SQLEnum(PositionType), nullable=False, default=PositionType.LONG)
    status : Mapped[PositionStatus] = mapped_column(SQLEnum(PositionStatus), nullable=False, default=PositionStatus.OPEN)
    realized_pnl : Mapped[float] = mapped_column(Numeric(20,8), default=0)
    closed_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    exit_price : Mapped[float] = mapped_column(Numeric(20, 8), default=0)

    # Relationship
    user : Mapped["User"] = relationship(back_populates="positions")
    trades : Mapped[list["Trade"]] = relationship(back_populates="position", lazy="selectin")
    '''
    This is a many-to-one relationship:
    Each Position belongs to exactly one User.

    Default lazy="select" is fine:

    One row → one query if accessed.

    Typically you are fetching a single User for a single Position.

    Using selectin here doesn’t make sense, because:

    selectin is designed for collections, i.e., multiple child rows per parent.

    Batching multiple parents → fetch all related children in one query.

    Since this is a scalar (single object), selectin is overkill.
    '''


    # Indexes for common queries
    __table_args__ = (
        Index("idx_positions_user_status", "user_id", "status"),
        Index("idx_positions_symbol_status", "symbol", "status"),
        Index("idx_positions_user_symbol", "user_id", "symbol"),
    )

    def calculate_unrealized_pnl(self, current_price: float) -> float:
        '''Calculate unrealized PnL given current price'''
        if self.position_type == PositionType.LONG:
            return float(self.quantity) * (float(current_price) - float(self.entry_price))
        else:
            return float(self.quantity) * (float(self.entry_price) - float(current_price))

    def calculate_pnl_percentage(self, current_price : float) -> float:
        unrealized = self.calculate_unrealized_pnl(current_price)
        invested = float(self.quantity * self.entry_price)

        if invested > 0:
            return (unrealized/invested)*100
        return 0.0

    def __repr__(self):
        return f"<Position {self.symbol} {self.quantity}@{self.entry_price}>"