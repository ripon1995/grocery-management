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

api_router = APIRouter()
api_router.include_router(grocery_router)
