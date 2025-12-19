"""
Application Entry Point

This script serves as the main entry point for running the Pro Trader
real-time trading platform in development mode.

Usage:
    python run.py

This will start the FastAPI application using Uvicorn ASGI server
with default development settings.

For production deployment, use:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

Or with Gunicorn for better production performance:
    gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
"""

import uvicorn


if __name__ == "__main__":
    # Start the FastAPI application using Uvicorn ASGI server
    # 
    # Configuration:
    # - app.main:app refers to the 'app' variable in app/main.py
    # - Default host: 127.0.0.1 (localhost only)
    # - Default port: 8000
    # - Auto-reload enabled in development mode
    # - Log level: info (shows request logs and application events)
    #
    # The application will be available at: http://localhost:8000
    # API documentation at: http://localhost:8000/docs
    # WebSocket endpoint at: ws://localhost:8000/ws
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )
