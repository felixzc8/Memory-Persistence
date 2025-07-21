# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TiMemory is a full-stack AI chatbot application with persistent memory capabilities. The system uses TiDB Vector database for semantic memory storage and maintains conversation context across sessions through a custom memory management system called TiMem.

## Architecture

### Backend (FastAPI + Python)
- **Main App**: `backend/app/main.py` - FastAPI application with middleware, routing, and lifecycle management
- **Core Memory System**: `backend/memory/timemory.py` - Custom TiMem class for memory extraction and consolidation
- **Database Layer**: `backend/app/db/database.py` - SQLAlchemy models and TiDB connection management
- **API Routes**: `backend/app/api/` - Chat endpoints (`chat.py`) and admin endpoints (`admin.py`)
- **Services**: `backend/app/services/` - Business logic for chat, memory, session, and user management
- **Configuration**: `backend/app/core/config.py` - Settings management using Pydantic with environment variables

### Frontend (React + Vite)
- **Main App**: `frontend/src/App.jsx` - React app with terminal-style chat interface
- **Components**: `frontend/src/components/` - Chat and Login components
- **Routing**: `frontend/src/router/AppRouter.jsx` - Client-side routing
- **Build Tool**: Vite with API proxy to backend on port 8000

### Memory Management Architecture
- **TiMem**: Custom memory management system using OpenAI for fact extraction and consolidation
- **TiDB Vector**: Vector database integration for semantic search and storage
- **Memory Flow**: Messages → Fact Extraction → Memory Consolidation → Vector Storage → Retrieval

## Development Commands

### Backend Setup and Running
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
uv sync  # Install dependencies (preferred)
# OR: pip install -r requirements.txt

# Run development server
python app/main.py
# OR: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup and Running
```bash
cd frontend
npm install
npm run dev    # Starts on http://localhost:5173
npm run build  # Production build
npm run preview  # Preview production build
```

## Environment Configuration

### Required Environment Variables (.env in backend/)
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
MODEL_CHOICE=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# TiDB Configuration  
TIDB_HOST=your_tidb_host
TIDB_PORT=4000
TIDB_USER=your_tidb_user
TIDB_PASSWORD=your_tidb_password
TIDB_DB_NAME=your_database_name

# Optional
LOGFIRE_TOKEN=your_logfire_token
```

## Key Technical Details

### Memory System
- Uses custom TiMem class for memory management
- Fact extraction from conversations using structured prompts
- Memory consolidation to resolve conflicts and duplicates
- Vector embeddings stored in TiDB Vector database
- Memory isolation per user_id for privacy

### API Architecture
- RESTful API design with `/api/v1/chat` prefix
- Streaming responses using Server-Sent Events (SSE)
- Session-based conversation management
- Comprehensive error handling with custom exception types
- CORS enabled for development

### Database Schema
- SQLAlchemy models in `backend/app/models/`
- User, Session, Message, and Memory models
- TiDB Serverless with SSL connection
- Vector table: `memories` (configurable via settings)

### Frontend Features
- Terminal-style UI with MacOS aesthetic
- Real-time streaming responses via EventSource API
- Username-based authentication with localStorage persistence
- Session management and conversation history

## Development Patterns

### Error Handling
- Custom exception classes in `app/core/exceptions/`
- Global exception handlers in `app/middleware/exception_handler.py`
- Request ID middleware for tracking

### Logging
- Logfire integration for structured logging
- SQLAlchemy query logging available
- FastAPI request/response logging

### Service Layer Pattern
- Business logic separated into service classes
- Dependency injection via FastAPI dependencies
- Clean separation of concerns: API → Service → Database/External

### Memory Prompts
- Structured prompts in `backend/memory/prompts.py`
- Pydantic models for memory schemas in `backend/memory/schemas/`
- OpenAI function calling for structured responses

## API Access
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Package Management
- Backend: Uses `uv` for fast dependency management (preferred) or pip with requirements.txt
- Frontend: npm with package.json
- Python: >= 3.9 required for backend
- Node.js: >= 16 required for frontend