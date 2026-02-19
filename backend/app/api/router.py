"""
Central place to plug feature routers.
"""

"""
HTTP request
   ↓
Router (HTTP layer)
   ↓
Service (business logic)
   ↓
Repository (DB access)
   ↓
Database
"""

from fastapi import APIRouter
from app.features.grocery.router import router as grocery_router
from app.features.auth.router import router as auth_router

api_router = APIRouter()
api_router.include_router(grocery_router)

api_router.include_router(auth_router)
