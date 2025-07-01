# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Then edit with your values
```

### Running the Application
```bash
# From backend directory
python run.py

# Alternative with uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Chat endpoint (requires proper TiDB/OpenAI configuration)
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_id": "test_user"}'
```

## Architecture Overview

This is a **backend-only** FastAPI application for an AI chatbot with persistent memory capabilities.

### Core Technologies
- **FastAPI** + **Uvicorn**: Web framework and ASGI server
- **OpenAI** (GPT-4o-mini default): Language model integration
- **Mem0**: Persistent memory management framework
- **TiDB Serverless**: Primary database (MySQL-compatible)
- **TiDB Vector**: Vector database for memory storage via LangChain
- **LangChain**: Vector store abstraction layer

### Directory Structure
```
backend/app/
├── main.py              # FastAPI app initialization and routes
├── config.py            # Settings management with Pydantic
├── api/chat.py          # Chat endpoints (/api/v1/chat, /api/v1/memories/*)
├── services/
│   ├── chat_service.py  # OpenAI integration
│   └── memory_service.py # Mem0 memory operations
└── schemas/chat.py      # Pydantic models for request/response
```

### Clean Architecture Pattern
- **API Layer**: FastAPI routes in `api/` handle HTTP requests
- **Service Layer**: Business logic in `services/` integrates external APIs
- **Schema Layer**: Pydantic models in `schemas/` validate data
- **Config Layer**: Centralized settings in `config.py`

## Key Implementation Details

### Memory Management
- Uses Mem0 with automatic user isolation via user_id
- Memories stored in TiDB Vector database via LangChain integration
- Each conversation maintains context through memory retrieval

### Database Configuration
- TiDB Serverless with SSL connection for regular database operations
- TiDB Vector for memory storage with cosine similarity (default)
- PyMySQL connector with SSL certificate validation
- Connection parameters: host, port, user, password, database name
- Vector table name: `memory_vectors` (configurable)

### API Endpoints
- `POST /api/v1/chat` - Main chat with memory
- `POST /api/v1/memories/search` - Search user memories  
- `GET /api/v1/memories/summary/{user_id}` - Conversation summary
- `DELETE /api/v1/memories/{user_id}` - Delete user memories
- `GET /health` and `GET /api/v1/health` - Health checks

### Environment Variables Required
```env
OPENAI_API_KEY=         # OpenAI API key
MODEL_CHOICE=           # OpenAI model (e.g., gpt-4o-mini)
TIDB_HOST=              # TiDB host
TIDB_PORT=4000          # TiDB port
TIDB_USER=              # TiDB username
TIDB_PASSWORD=          # TiDB password
TIDB_DB_NAME=           # TiDB database name
```

## Current Status
- Authentication middleware removed (auth_middleware.py deleted)
- Frontend removed (was React Native)
- Recent changes to config, memory service, and API endpoints
- No test suite or CI/CD pipeline currently implemented