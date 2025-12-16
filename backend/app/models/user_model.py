from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from app.db.base_db import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass
