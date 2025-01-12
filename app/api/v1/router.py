# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import documents, analysis

api_router = APIRouter()

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)

api_router.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["analysis"]
)