import uuid
from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User Model"""

    __tablename__ = "users"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),default=uuid.uuid4, primary_key=True)
    email : Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username : Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash : Mapped[str] = mapped_column(String(255), nullable=False)
    is_active : Mapped[bool] = mapped_column(default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationship

    

    def __repr__(self):
        return f"<User {self.username}"