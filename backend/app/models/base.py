from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    "Mixin for created_at and updated_at timestamps"

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True) ,default=datetime.now(ZoneInfo("UTC")), nullable=False)
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.now(ZoneInfo("UTC")), nullable=False)