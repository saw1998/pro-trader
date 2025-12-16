
from fastapi_users import FastAPIUsers

from app.auth.jwt.user_manager import get_user_manager
from app.auth.jwt.auth_backend import auth_backend


auth_users = FastAPIUsers(
    get_user_manager,
    [auth_backend],
)


current_user = auth_users.current_user()

