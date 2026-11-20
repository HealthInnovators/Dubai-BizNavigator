"""API V1 Router."""

from fastapi import APIRouter

from app.interfaces.api.v1.endpoints import business, health

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(business.router)
