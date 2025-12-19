
"""
Main API Router Module

This module aggregates all API route modules into a single router that gets
included in the main FastAPI application. It provides a centralized place
to manage API versioning and route organization.

The router uses the "/api/v1" prefix to support API versioning, allowing
future versions (v2, v3, etc.) to coexist with the current implementation.
"""

from fastapi import APIRouter

# Import all API route modules
from app.api import auth, positions


# Create the main API router with version prefix
# This allows for clean URL structure: /api/v1/auth/*, /api/v1/positions/*
router = APIRouter(prefix="/api/v1")

# Include authentication routes
# Handles: /api/v1/auth/register, /api/v1/auth/login, /api/v1/auth/logout, /api/v1/auth/me
router.include_router(auth.router)

# Include position management routes  
# Handles: /api/v1/positions/, /api/v1/positions/{id}, /api/v1/positions/{id}/close
router.include_router(positions.router)
