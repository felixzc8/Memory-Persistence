from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.chat import router as chat_router
from app.api.admin import router as admin_router
from app.config import settings
from app.database import create_tables

app = FastAPI(
    title="TiDB + Mem0 Chatbot API",
    description="A FastAPI backend for a persistent memory chatbot using OpenAI and Mem0 with TiDB Serverless with Session Management",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    create_tables()

app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "Chatbot API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}