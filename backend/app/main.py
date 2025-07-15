from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.admin import router as admin_router
from app.config import settings
from app.database import create_tables
from app.services.cleanup_service import cleanup_service
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    await cleanup_service.start_cleanup_task()
    yield
    # Shutdown
    await cleanup_service.stop_cleanup_task()

app = FastAPI(
    title="TiDB + Mem0 Chatbot API",
    description="A FastAPI backend for a persistent memory chatbot using OpenAI and Mem0 with TiDB Serverless with Session Management",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "Homi Chatbot API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
