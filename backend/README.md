# Project Structure

- **my_fastapi_app/**
  - **app/**
    - `__init__.py`
    - `main.py` — FastAPI app instance and startup
    - **core/** — Core settings and utilities
      - `__init__.py`
      - `config.py` — App config, environment variables
      - `security.py` — JWT, password hashing, authentication utils
      - `logging.py` — Logging setup
    - **api/** — API routes
      - `__init__.py`
      - **v1/** — Versioned API
        - `__init__.py`
        - **endpoints/** — API endpoint modules
          - `__init__.py`
          - `users.py`
          - `items.py`
        - `dependencies.py` — Route dependencies
      - **v2/** — Future API version
    - **models/** — SQLAlchemy / ORM models
      - `__init__.py`
      - `user.py`
      - `item.py`
    - **schemas/** — Pydantic schemas for requests/responses
      - `__init__.py`
      - `user.py`
      - `item.py`
    - **crud/** — Database operations (create, read, update, delete)
      - `__init__.py`
      - `user.py`
      - `item.py`
    - **db/** — Database setup
      - `__init__.py`
      - `base.py` — Base class for models
      - `session.py` — Database connection/session
      - `init_db.py` — Optional DB initialization script
    - **services/** — Business logic / background tasks
      - `__init__.py`
      - `notifications.py`
    - **websocket/** — WebSocket handlers and connection managers
      - `__init__.py`
      - `manager.py`
    - **utils/** — Helper functions and shared utilities
      - `__init__.py`
      - `helpers.py`
  - **tests/** — Unit and integration tests
    - `__init__.py`
    - `test_users.py`
    - `test_items.py`
  - **alembic/** — Optional: Database migrations
  - `requirements.txt` — Python dependencies
  - `.env` — Environment variables
  - `README.md`

---

## Design Principles

- **Separation of concerns**
  - `models` → database models
  - `schemas` → request/response validation
  - `crud` → database operations
  - `services` → business logic
  - `api` → routes

- **Versioned APIs**
  - Use folders like `/api/v1/` and `/api/v2/` to maintain multiple versions without breaking existing clients.

- **Extendability**
  - Adding a new feature is easy: create new modules in `api/endpoints`, `models`, `schemas`, `crud`, and `services`.

- **Centralized configuration**
  - All app-wide settings and secrets are in `/core/config.py`.

- **Testing-friendly**
  - `/tests` mirrors your `app` structure for easier unit and integration testing.

- **WebSockets and background tasks**
  - Keep WebSocket managers in `/websocket/` and background tasks in `/services/`.
