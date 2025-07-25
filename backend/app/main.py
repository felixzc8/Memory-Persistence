import logging
from logging import basicConfig
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.chat import router as chat_router
from app.api.v1.admin import router as admin_router
from app.core.config import settings
from app.db.database import create_tables
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.exception_handler import (
    database_exception_handler,
    validation_exception_handler,
    chat_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from app.core.exceptions import DatabaseException, ValidationException, ChatException
from contextlib import asynccontextmanager
import logfire

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield
    pass

app = FastAPI(
    title="TiDB Vector Memory Chatbot API",
    description="TiMemory",
    version="2.0.0",
    lifespan=lifespan
)

logfire.configure(token=settings.logfire_token)
basicConfig(handlers=[logfire.LogfireLoggingHandler()], level=logging.INFO)
logfire.instrument_fastapi(app, capture_headers=True)


logger = logging.getLogger(__name__)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(DatabaseException, database_exception_handler)
app.add_exception_handler(ValidationException, validation_exception_handler)
app.add_exception_handler(ChatException, chat_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "Chatbot API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_config=None,
        log_level=None,
    )
