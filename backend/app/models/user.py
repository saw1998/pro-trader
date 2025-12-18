import uuid
from sqlalchemy import UUID, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User Model"""

    __tablename__ = "users"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),default=uuid.uuid4, primary_key=True)
    email : Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username : Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash : Mapped[str] = mapped_column(String(255), nullable=False)
    is_active : Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationship
    positions: Mapped[list["Position"]] = relationship(back_populates="user", lazy="selectin")
    trades : Mapped[list["Trade"]] = relationship(back_populates="user", lazy="selectin")  

    def __repr__(self):
        return f"<User {self.username}"


'''
Models
User -> Position (one-to-many)

❌ Bad case (lazy="select" – default)
users = session.execute(select(User)).scalars().all()

for user in users:
    print(user.positions)

SQL executed
-- 1 query
SELECT * FROM user;

-- N queries (one per user)
SELECT * FROM position WHERE user_id = 1;
SELECT * FROM position WHERE user_id = 2;
SELECT * FROM position WHERE user_id = 3;
...


If:

100 users → 101 queries

1,000 users → 1,001 queries

🚨 This kills performance.

Why this is bad

Many network round-trips

High DB load

Slow response times

Gets worse as data grows

How lazy="selectin" avoids it
positions = relationship(lazy="selectin")

What happens instead
-- 1 query for users
SELECT * FROM user;

-- 1 query for ALL related positions
SELECT * FROM position WHERE user_id IN (1, 2, 3, ...);


Total queries = 2, no matter how many users.

✅ This is why we say “avoids the N+1 query problem”.

Visual comparison
Pattern	Queries
N+1	1 + N
selectin	2
joined	1 (with JOIN)

'''