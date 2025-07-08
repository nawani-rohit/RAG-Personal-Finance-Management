from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Personal Finance Management RAG API",
        "version": settings.VERSION,
        "docs": "/docs",
        "api_base": settings.API_V1_STR,
        "endpoints": {
            "upload_document": f"{settings.API_V1_STR}/documents/upload/",
            "list_documents": f"{settings.API_V1_STR}/documents/list/",
            "query_documents": f"{settings.API_V1_STR}/analysis/query/"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Personal Finance Management RAG API"}

app.include_router(api_router, prefix=settings.API_V1_STR)