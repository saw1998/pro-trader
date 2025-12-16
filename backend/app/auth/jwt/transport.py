from fastapi_users.authentication import BearerTransport

# login url
bearer_transport = BearerTransport(tokenUrl="auth/login")