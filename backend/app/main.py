from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.config import settings

app = FastAPI(
    title="Homi Chatbot API",
    description="A FastAPI backend for a persistent memory chatbot using OpenAI and Mem0",
    version="1.0.0"
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
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Homi Chatbot API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
