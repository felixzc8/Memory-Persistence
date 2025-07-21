# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (FastAPI + Python)
- `cd backend && python app/main.py` - Run the backend server directly
- `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` - Run with uvicorn in reload mode
- `cd backend && uv install` - Install dependencies using uv package manager
- `cd backend && pip install -r requirements.txt` - Install dependencies using pip

### Frontend (React + Vite)  
- `cd frontend && npm run dev` - Start development server
- `cd frontend && npm run build` - Build for production
- `cd frontend && npm run preview` - Preview production build

### Project Setup
- Backend uses `.env` file for configuration (see `.env.example` for template)
- TiDB database connection required with SSL configuration
- OpenAI API key required for LLM and embedding services
- Logfire token optional for observability

## Architecture Overview

### TiMemory Core System
The project implements TiMemory, a persistent memory chatbot using TiDB vector database:

- **Memory Processing Pipeline**: `backend/memory/timemory.py` - Core memory extraction, consolidation, and storage
- **Vector Storage**: `backend/memory/tidb_vector.py` - TiDB vector database operations  
- **LLM Integration**: `backend/memory/llms/openai.py` - OpenAI chat completion wrapper
- **Embeddings**: `backend/memory/embedding/openai.py` - Text embedding generation

### FastAPI Backend Structure
- **Main App**: `backend/app/main.py` - FastAPI application with middleware and routing
- **Routers**: `backend/app/routers/` - API endpoints for chat and admin functions
- **Services**: `backend/app/services/` - Business logic layer (chat, memory, user, session services)  
- **Models**: `backend/app/models/` - SQLAlchemy database models
- **Schemas**: `backend/app/schemas/` - Pydantic data validation models
- **Dependencies**: `backend/app/dependencies/` - FastAPI dependency injection (auth, validation, session)
- **Middleware**: `backend/app/middleware/` - Request ID tracking and exception handling

### Key Technologies
- **Database**: TiDB with vector search capabilities via PyTiDB
- **Backend**: FastAPI with SQLAlchemy ORM
- **Frontend**: React with Vite
- **Memory System**: Custom TiMemory implementation using OpenAI embeddings
- **Observability**: Logfire integration for logging and monitoring

### Memory System Flow
1. **Message Processing**: Extract facts from user-AI conversations using LLM
2. **Similarity Search**: Find related existing memories using vector search
3. **Memory Consolidation**: Merge new and existing memories to avoid duplication  
4. **Storage**: Store consolidated memories with embeddings in TiDB

### Authentication & Security
- JWT-based authentication with user isolation
- All chat and memory endpoints require authentication
- Admin endpoints for user/session management
- Password hashing with bcrypt

## Configuration Requirements
- TiDB connection string with SSL certificates
- OpenAI API key for chat and embeddings
- JWT secret for authentication
- Optional Logfire token for observability

The system is designed for production deployment with Docker support and comprehensive error handling.