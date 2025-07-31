# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the TiMemory project.

## Project Overview

TiMemory is an advanced AI chatbot system with persistent memory capabilities built on three main components:

1. **TiMemory Core Engine** (`TiMemory/`) - Standalone memory processing package
2. **FastAPI Backend** (`backend/`) - Web API and business logic layer  
3. **React Frontend** (`frontend/`) - User interface with real-time chat

## Development Commands

### TiMemory Core System
- `cd TiMemory && uv install` - Install core memory system dependencies
- `cd TiMemory && uv sync` - Sync virtual environment with lock file
- `cd TiMemory && uv run python -c "from timemory import TiMemory; # test functionality"` - Test core system
- `cd TiMemory && uv run celery -A celery_app worker --loglevel=info` - Start background memory processing workers

### Backend (FastAPI + Python)
- `cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` - Run development server with hot reload
- `cd backend && uv run python app/main.py` - Run backend server directly using built-in uvicorn
- `cd backend && uv install` - Install backend dependencies from pyproject.toml
- `cd backend && uv sync` - Sync virtual environment with lock file
- `cd backend && uv add <package>` - Add new dependency to backend
- `cd backend && uv run python -c "from app.db.database import create_tables; create_tables()"` - Initialize database tables

### Frontend (React + Vite)  
- `cd frontend && npm run dev` - Start Vite development server (http://localhost:5173)
- `cd frontend && npm run build` - Build for production
- `cd frontend && npm run preview` - Preview production build
- `cd frontend && npm install` - Install frontend dependencies

### Docker Deployment
- `docker-compose up --build` - Run entire stack (frontend: http://localhost:3000, backend: http://localhost:8000)
- `docker build -t timemory-backend ./backend` - Build backend image
- `docker build -t timemory-frontend ./frontend` - Build frontend image

### Environment Setup
Both TiMemory core and backend require `.env` files:
- `cp TiMemory/.env.example TiMemory/.env` - Configure core memory system with Redis settings
- `cp backend/.env.example backend/.env` - Configure backend API
- Ensure Redis server is running: `redis-server` (install via `brew install redis` on macOS)
- `cp TiMemory/.env.example TiMemory/.env` - Configure core memory system
- `cp backend/.env.example backend/.env` - Configure backend API

## Architecture Overview

### TiMemory Core Memory System
The heart of the project is a sophisticated AI-powered memory processing pipeline:

- **Memory Processing Pipeline** (`TiMemory/timemory.py`):
  1. **Extract**: AI-powered fact extraction from conversations using LLM with structured Pydantic output
  2. **Search**: Vector similarity search against existing memories using 1536-dimensional OpenAI embeddings
  3. **Consolidate**: LLM-driven memory conflict resolution and intelligent merging
  4. **Store**: Persistent storage in TiDB with vector embeddings and user isolation

  5. **Background Processing**: Redis + Celery workers for non-blocking memory operations

- **Vector Database Operations** (`TiMemory/tidb_vector.py`): TiDB vector database wrapper with cosine similarity search
- **LLM Integration** (`TiMemory/llms/openai.py`): OpenAI chat completion wrapper with structured output parsing
- **Embeddings** (`TiMemory/embedding/openai.py`): OpenAI text-embedding-3-small integration (1536 dimensions)

- **Background Workers** (`TiMemory/workers/`): Celery task queue for asynchronous memory processing

- **Configuration** (`TiMemory/config/base.py`): Pydantic settings with environment variable support

### FastAPI Backend Architecture
- **Main App** (`backend/app/main.py`): FastAPI application with Logfire observability, CORS, and lifespan management
- **API Layer** (`backend/app/api/v1/`): RESTful endpoints for chat and admin operations
  - **Chat API** (`chat.py`): Streaming chat, session management, memory operations
  - **Admin API** (`admin.py`): Administrative endpoints (minimal structure)
- **Services** (`backend/app/services/`): Business logic layer
  - **Chat Service** (`chat_service.py`): Chat processing with memory integration and streaming support
  - **Memory Service** (`memory_service.py`): TiMemory system wrapper for web API
  - **User Service** (`user_service.py`): User authentication and validation  
  - **Session Service** (`session_service.py`): Session creation, management, and metadata
- **Models** (`backend/app/models/`): SQLAlchemy database models with TiDB vector support
- **Schemas** (`backend/app/schemas/`): Pydantic request/response validation models
- **Dependencies** (`backend/app/dependencies/`): FastAPI dependency injection for auth, validation, session management
- **Middleware** (`backend/app/middleware/`): Request ID tracking and comprehensive exception handling
- **Database** (`backend/app/db/database.py`): SQLAlchemy configuration with SSL-enabled TiDB connections

### React Frontend Architecture
- **Main App** (`frontend/src/App.jsx`): Root component with global styling
- **Routing** (`frontend/src/router/AppRouter.jsx`): Client-side routing with authentication state management
- **Components** (`frontend/src/components/`):
  - **Login** (`Login.jsx`): Username-based authentication with localStorage persistence
  - **Chat** (`Chat.jsx`): Real-time chat interface with Server-Sent Events streaming
  - **ApiLogPanel** (`ApiLogPanel.jsx`): Development debugging panel
- **Contexts** (`frontend/src/contexts/`): React context providers for state management
- **Styles** (`frontend/src/styles/`): Terminal-style CSS with monospace fonts and dark theme

## Key Technologies

### Core Dependencies
- **Database**: TiDB with vector search capabilities via tidb-vector and PyMySQL
- **Backend**: FastAPI with SQLAlchemy ORM, uvicorn ASGI server
- **Frontend**: React 18 with Vite build tool
- **Memory System**: Custom TiMemory implementation using OpenAI embeddings and LLM processing
- **Package Management**: UV for Python, npm for Node.js
- **Observability**: Logfire integration for logging, monitoring, and performance tracking

### Memory System Technologies
- **Vector Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **LLM Processing**: OpenAI gpt-4o-mini for structured fact extraction and memory consolidation
- **Vector Database**: TiDB with native vector operations and cosine similarity search
- **Memory Categories**: 7 semantic categories (personal, preference, activity, plan, health, professional, miscellaneous)
- **Memory Status**: Active/outdated status system for "forgetting" rather than deletion

### API Features
- **Content Negotiation**: JSON responses or Server-Sent Events streaming based on Accept header
- **Memory Operations**: Search, summarization, and deletion endpoints
- **Session Management**: Create, list, update, delete conversation sessions
- **Real-time Streaming**: Incremental AI response delivery via EventSource
- **User Isolation**: Complete data separation at database level with user_id indexing

## Configuration Requirements

### Environment Variables

**TiMemory Core (`.env` in TiMemory/):**
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
MODEL_CHOICE=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_MODEL_DIMS=1536

# TiDB Configuration
TIDB_HOST=your_tidb_host
TIDB_PORT=4000
TIDB_USER=your_username
TIDB_PASSWORD=your_password
TIDB_DB_NAME=your_database_name
TIDB_USE_SSL=true
TIDB_VERIFY_CERT=true
TIDB_SSL_CA=/path/to/ca-cert.pem

# Memory System Settings
MEMORY_COLLECTION_NAME=memories
MEMORY_SEARCH_LIMIT=10
MESSAGE_LIMIT=20
SUMMARY_THRESHOLD=10
```

**Backend API (`.env` in backend/):**
```env
# Inherits all TiMemory configuration plus:
LOGFIRE_TOKEN=your_logfire_token_for_observability
```

### TiDB Database Setup
1. Create TiDB Cloud cluster with vector search enabled
2. Configure SSL certificates for secure connections
3. Create database and enable vector operations
4. Ensure user has appropriate permissions for CREATE TABLE operations
5. Update connection parameters in both environment files

## Memory System Flow

### Memory Processing Pipeline
1. **Message Input**: User-AI conversation pairs are analyzed
2. **Fact Extraction**: LLM extracts structured facts using Pydantic schemas for validation
3. **Similarity Search**: New memories compared against existing ones using vector embeddings
4. **Memory Consolidation**: LLM intelligently merges related memories and resolves conflicts
5. **Vector Storage**: Consolidated memories stored with embeddings in TiDB for future retrieval

### Advanced Memory Features
- **Cross-Referential Inference**: Extracts implied facts from multi-turn conversations
- **Memory Forgetting**: Marks outdated memories as "outdated" rather than deleting them
- **Temporal Context**: Handles time-sensitive preference changes and planning information
- **Semantic Categorization**: Automatically categorizes memories by type for better organization
- **Conflict Resolution**: LLM-driven resolution of contradictory memory information

### Authentication & Security
- **Simple Authentication**: Username-based system with localStorage persistence
- **User Isolation**: All database queries filtered by user_id with indexed partitioning
- **SSL Connections**: All database connections use SSL with certificate verification
- **Input Validation**: Comprehensive Pydantic schema validation for all API endpoints
- **Request Tracking**: UUID-based request correlation across all services
- **Error Sanitization**: Structured error responses without internal system details

## Development Workflow

### Adding New Memory Features
1. Update memory schemas in `TiMemory/schemas/`
2. Extend memory processing logic in `TiMemory/timemory.py`
3. Add new API endpoints in `backend/app/api/v1/chat.py`
4. Update backend services in `backend/app/services/`
5. Test vector search and storage functionality
6. Update frontend components if UI changes needed

### Adding New API Endpoints
1. Define request/response schemas in `backend/app/schemas/`
2. Implement business logic in appropriate service (`backend/app/services/`)
3. Create API endpoint in `backend/app/api/v1/`
4. Add authentication/validation dependencies
5. Consider content negotiation for multiple response types
6. Update error handling and logging

### Frontend Development
1. Create components in `frontend/src/components/`
2. Add styles in `frontend/src/styles/` following terminal aesthetic
3. Update routing logic in `AppRouter.jsx` if needed
4. Implement API integration with proper error handling
5. Add loading states and real-time updates
6. Test streaming functionality with Server-Sent Events

### Testing and Validation
- Backend API can be tested directly via curl or tools like Postman
- Frontend development server proxies API calls to backend automatically
- Use browser DevTools Network tab to monitor streaming events
- Check database directly for memory storage and vector operations
- Monitor Logfire for observability data if configured

## Key Files Reference

**Core Memory System:**
1. `TiMemory/timemory.py` - Main memory processing pipeline
2. `TiMemory/tidb_vector.py` - Vector database operations wrapper
3. `TiMemory/config/base.py` - Configuration management with Pydantic
4. `TiMemory/MEMORY.md` - Detailed technical architecture documentation

**Backend:**
1. `backend/app/main.py` - FastAPI application entry point
2. `backend/app/api/v1/chat.py` - Primary chat API endpoints
3. `backend/app/services/chat_service.py` - Chat business logic with streaming
4. `backend/app/core/config.py` - Backend configuration and settings
5. `backend/CLAUDE.md` - Detailed backend development guide

**Frontend:**
1. `frontend/src/router/AppRouter.jsx` - Authentication and routing
2. `frontend/src/components/Chat.jsx` - Real-time chat interface
3. `frontend/src/components/Login.jsx` - Authentication interface
4. `frontend/vite.config.js` - Build configuration and API proxy
5. `frontend/CLAUDE.md` - Frontend development guide

## Common Development Tasks

### Running Full Development Stack
```bash
# Terminal 1: Start Redis server
redis-server

# Terminal 2: Start TiMemory background workers
cd TiMemory && uv run celery -A celery_app worker --loglevel=info

# Terminal 3: Start backend server
cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 4: Start frontend server  
cd frontend && npm run dev
```

### Database Operations
```bash
# Initialize database tables
cd backend && uv run python -c "from app.db.database import create_tables; create_tables()"

# Test database connection
cd backend && uv run python -c "from app.core.config import settings; print(settings.tidb_connection_string)"
```

### Debugging and Monitoring
- Check backend logs for API request processing and errors
- Monitor Logfire dashboard if token is configured
- Use browser DevTools for frontend debugging and network monitoring
- Check TiDB console for database query performance and vector operations

The system is designed for production deployment with Docker support, comprehensive error handling, and observability integration. All components are configured for development with hot reload and can be deployed individually or as a complete stack.