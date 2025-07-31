# CLAUDE.md - Backend

This file provides guidance to Claude Code (claude.ai/code) when working with the TiMemory FastAPI backend.

## Development Commands

### Running the Application
- `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` - Start development server with hot reload
- `uv run python app/main.py` - Run the app directly using the built-in uvicorn launcher
- `uv install` - Install all dependencies from pyproject.toml and create/update uv.lock
- `uv sync` - Sync the virtual environment with the lock file
- `uv add <package>` - Add new dependencies
- `uv remove <package>` - Remove dependencies

### Database Operations
- `uv run python -c "from app.db.database import create_tables; create_tables()"` - Initialize database tables
- `uv run python -c "from app.core.config import settings; print(settings.tidb_connection_string)"` - Test database connection

## Project Structure

### FastAPI Application Architecture

**Main Application (`app/main.py`)**
- **FastAPI App**: Configured with title "TiDB Vector Memory Chatbot API", version 2.0.0
- **Middleware Stack**:
  - `RequestIDMiddleware` - UUID tracking for request correlation
  - `CORSMiddleware` - Frontend integration with full CORS support
- **Exception Handlers**: Custom handlers for DatabaseException, ValidationException, ChatException, HTTPException, and general exceptions
- **Observability**: Logfire integration for monitoring and logging with structured logging
- **Lifespan Management**: Database table creation on startup via asynccontextmanager

**API Layer (`app/api/v1/`)**
- **Chat Router** (`chat.py`): Primary API endpoints for chat functionality, session management, and memory operations
- **Admin Router** (`admin.py`): Administrative endpoints (minimal structure for future expansion)

**Services Layer (`app/services/`)**

**Chat Service (`chat_service.py`)**:
- `chat_with_memory()` - Standard chat with TiMemory integration for context-aware responses
- `chat_with_memory_stream()` - Streaming chat responses using Server-Sent Events
- `get_conversation_summary()` - AI-generated conversation summaries
- OpenAI integration with configurable models (gpt-4o-mini default)

**Memory Service (`memory_service.py`)**:
- TiMemory system wrapper for FastAPI integration
- Vector search capabilities for user memories with similarity thresholds
- Memory deletion and management operations
- Direct integration with TiMemory core engine

**User Service (`user_service.py`)**:
- Simple username-based authentication and validation
- Database health checking functionality
- User activity tracking and session management

**Session Service (`session_service.py`)**:
- Session creation with AI-generated titles using TiMemory session manager
- Session metadata management (update, delete operations)
- User session listing and retrieval with pagination support

### Data Models and Schemas

**Pydantic Schemas (`app/schemas/`)**:
- `ChatRequest` / `ChatResponse` - Chat message request/response structures
- `Session` / `SessionListResponse` / `UpdateSessionRequest` - Session management (imported from TiMemory)
- `User` - User profile and authentication data
- `ErrorResponse` - Structured error response models

**SQLAlchemy Models (`app/models/`)**:
- `User` - User accounts with timestamps and authentication data
- Additional models imported from TiMemory core system (Session, Memory, etc.)

### Dependencies (`app/dependencies/`)

**Authentication (`auth.py`)**:
- `get_authenticated_user()` - Simple user ID validation (no JWT currently)
- Username-based authentication system with future expansion capabilities

**Session Management (`session.py`)**:
- `get_user_session()` - Session ownership verification
- Session existence and access validation with user isolation

**Validation (`validation.py`)**:
- `validate_chat_request()` - Chat input validation with Pydantic schemas
- `validate_memory_search_request()` - Search input validation

**Memory Integration (`memory.py`)**:
- `get_available_memory_service()` - Memory service dependency injection
- Integration point with TiMemory core system

### Middleware (`app/middleware/`)

**Request ID Tracking (`request_id.py`)**:
- Generates UUID for each request for correlation across logs
- Enables request tracking through distributed system
- Adds request ID to response headers for debugging

**Exception Handling (`exception_handler.py`)**:
- `DatabaseException` - Database connectivity and query errors with user-friendly messages
- `ValidationException` - Input validation failures with detailed error information
- `ChatException` - LLM and chat processing errors
- `HTTPException` - Standard HTTP errors with structured responses
- `General Exception Handler` - Catch-all for unexpected errors
- Structured error responses with error codes and request IDs

### Configuration (`app/core/config.py`)

**Settings Class**: Inherits from TiMemory.config.base.MemoryConfig
- **OpenAI Configuration**: API key, model selection (gpt-4o-mini), embeddings (text-embedding-3-small)
- **TiDB Settings**: Host, port, credentials, database name, SSL configuration
- **API Settings**: Host (0.0.0.0), port (8000), debug mode (True)
- **Observability**: Logfire token for monitoring and structured logging

**Key Properties**:
- Inherits `tidb_connection_string` from MemoryConfig with SSL support
- Environment variable loading with .env file support
- Protected namespaces configuration for Pydantic

### Database Integration (`app/db/`)

**Database Connection (`database.py`)**:
- SQLAlchemy engine configuration with TiMemory integration
- SSL-enabled TiDB connections using inherited configuration
- Automatic table creation utilities via create_tables()
- Connection pooling and session management

## API Documentation

### Chat Endpoints (`/api/v1/chat`)

**POST** `/{user_id}/new` - Create new chat session
- Creates new session with AI-generated title
- Processes first message with memory integration
- **Content Negotiation**: 
  - `Accept: application/json` → Returns `ChatResponse` JSON object
  - `Accept: text/event-stream` → Returns streaming response via Server-Sent Events

```bash
# JSON response
curl -X POST "http://localhost:8000/api/v1/chat/user123/new" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"message": "Hello!", "user_id": "user123"}'

# Response:
{
  "response": "Hello! How can I help you today?",
  "user_id": "user123",
  "session_id": "uuid-string",
  "memories_used": [],
  "timestamp": "2024-01-15T10:30:00Z"
}

# Streaming response
curl -X POST "http://localhost:8000/api/v1/chat/user123/new" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "Tell me a story", "user_id": "user123"}'

# Response (Server-Sent Events):
event: session_created
data: {"session_id": "uuid-string", "title": "Tell me a story"}

event: content
data: {"content": "Once"}

event: content
data: {"content": " upon a time..."}

event: complete
data: {"session_id": "uuid-string"}
```

**POST** `/{user_id}/{session_id}` - Continue existing chat session
- Processes message within existing session context
- Integrates with TiMemory for contextual responses
- Supports both JSON and streaming responses

```bash
# Continue existing chat session
curl -X POST "http://localhost:8000/api/v1/chat/user123/session-uuid-123" \
  -H "Content-Type: application/json" \
  -d '{"message": "What did we talk about earlier?", "user_id": "user123"}'

# Response:
{
  "response": "Earlier we discussed...",
  "user_id": "user123",
  "session_id": "session-uuid-123",
  "memories_used": ["User asked about previous topics"],
  "timestamp": "2024-01-15T10:35:00Z"
}
```

**GET** `/{user_id}/sessions` - List user sessions
- Returns paginated list of user's chat sessions
- Includes session metadata, message counts, and activity timestamps

```bash
# List user sessions
curl -X GET "http://localhost:8000/api/v1/chat/user123/sessions"

# Response:
{
  "sessions": [
    {
      "session_id": "session-uuid-123",
      "user_id": "user123",
      "title": "Story Discussion",
      "created_at": "2024-01-15T10:30:00Z",
      "last_activity": "2024-01-15T10:35:00Z",
      "message_count": 4
    }
  ],
  "user_id": "user123",
  "total_count": 1
}
```

**GET** `/{user_id}/sessions/{session_id}` - Get specific session
- Returns complete session details including message history
- User isolation enforced at database level

```bash
# Get specific session details
curl -X GET "http://localhost:8000/api/v1/chat/user123/sessions/session-uuid-123"

# Response:
{
  "session_id": "session-uuid-123",
  "user_id": "user123",
  "title": "Story Discussion",
  "messages": [
    {
      "role": "user",
      "content": "Tell me a story",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Once upon a time...",
      "timestamp": "2024-01-15T10:30:15Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "last_activity": "2024-01-15T10:35:00Z",
  "message_count": 2
}
```

**PUT** `/{user_id}/sessions/{session_id}` - Update session metadata
- Allows updating session title and other metadata
- User ownership validation enforced

```bash
# Update session title
curl -X PUT "http://localhost:8000/api/v1/chat/user123/sessions/session-uuid-123" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Favorite Story Session"}'

# Response:
{
  "message": "Session updated successfully"
}
```

**DELETE** `/{user_id}/sessions/{session_id}` - Delete session
- Removes session and all associated messages
- User ownership validation enforced

```bash
# Delete session
curl -X DELETE "http://localhost:8000/api/v1/chat/user123/sessions/session-uuid-123"

# Response:
{
  "message": "Session deleted successfully"
}
```

### Memory Operations

**POST** `/{user_id}/memories/search` - Search user memories
- Vector similarity search using TiMemory core system
- Returns relevant memories based on query embedding

```bash
# Search user memories
curl -X POST "http://localhost:8000/api/v1/chat/user123/memories/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "programming languages",
    "user_id": "user123",
    "limit": 5
  }'

# Response:
{
  "memories": [
    "User prefers Python for data analysis projects",
    "User is learning JavaScript for web development"
  ],
  "user_id": "user123",
  "query": "programming languages"
}
```

**GET** `/{user_id}/memories/summary` - Get conversation summary
- AI-generated summary of user's conversation history and preferences

```bash
# Get conversation summary
curl -X GET "http://localhost:8000/api/v1/chat/user123/memories/summary"

# Response:
{
  "user_id": "user123",
  "summary": "This user is a software developer interested in data analysis and web development."
}
```

**DELETE** `/{user_id}/memories` - Delete all user memories
- Clears all memory data for the specified user
- Irreversible operation with user confirmation

```bash
# Delete all user memories
curl -X DELETE "http://localhost:8000/api/v1/chat/user123/memories"

# Response:
{
  "message": "Memories deleted for user user123"
}
```

### System Endpoints

**GET** `/health` - Service health check
- Returns comprehensive health status for all system components

```bash
# Check service health
curl -X GET "http://localhost:8000/api/v1/chat/health"

# Response:
{
  "status": "healthy",
  "service": "chat",
  "vector_store": "healthy",
  "database": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**GET** `/` - Root endpoint
- Basic service availability check

```bash
# Basic health check
curl -X GET "http://localhost:8000/"

# Response:
{
  "message": "Chatbot API is running!"
}
```

### Admin Endpoints (`/api/v1/admin`)
- Currently minimal structure for future administrative functions
- Placeholder for user management, system monitoring, and configuration endpoints

## TiMemory Integration

### Memory Service Integration
The backend integrates directly with the TiMemory core system:

- **Memory Processing**: Automatic fact extraction from conversations
- **Vector Search**: Similarity-based memory retrieval using OpenAI embeddings
- **Memory Consolidation**: Intelligent merging of related memories
- **Session Management**: AI-powered session title generation and organization

### Configuration Inheritance
Backend configuration inherits from TiMemory core settings:
- Database connection parameters
- OpenAI API configuration
- Memory processing settings
- Vector embedding parameters

## Development Workflow

### Adding New API Endpoints
1. Define request/response schemas in `app/schemas/`
2. Implement business logic in appropriate service (`app/services/`)
3. Create API endpoint in `app/api/v1/`
4. Add authentication and validation dependencies
5. Consider content negotiation if multiple response types needed
6. Update comprehensive error handling and logging
7. Test with both JSON and streaming responses where applicable

### Extending Memory Functionality
1. Update memory operations in TiMemory core system first
2. Extend memory service methods in `app/services/memory_service.py`
3. Add new API endpoints for memory operations
4. Test vector search and storage functionality
5. Update frontend integration if UI changes are needed

### Error Handling Best Practices
- Use appropriate custom exception types from `app.core.exceptions`
- Include request IDs in error responses for correlation
- Log errors with structured data for Logfire observability
- Provide meaningful error messages for API consumers
- Sanitize internal system details from user-facing errors

### Security Considerations
- All chat endpoints require user authentication via `get_authenticated_user`
- Session endpoints validate user ownership via `get_user_session`
- Memory operations are user-isolated at database level
- SSL-enabled database connections with certificate verification
- Comprehensive input validation on all endpoints using Pydantic schemas

## Performance Optimizations

### Database Performance
- Connection pooling with SQLAlchemy
- User-isolated queries with indexed user_id fields
- Vector operations optimized with TiDB native vector support
- Deferred loading of large vector columns in search results

### API Performance
- Streaming responses for real-time chat experience
- Async/await pattern throughout for non-blocking operations
- Request correlation with UUID tracking
- Efficient JSON serialization with Pydantic

### Observability
- Logfire integration for structured logging and monitoring
- Request/response timing and performance metrics
- Database query performance tracking
- Error rate monitoring and alerting capabilities

## Environment Configuration

### Required Environment Variables (.env file):
```env
# OpenAI Configuration (inherited from TiMemory)
OPENAI_API_KEY=your_openai_api_key
MODEL_CHOICE=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# TiDB Configuration (inherited from TiMemory)
TIDB_HOST=your_tidb_host
TIDB_PORT=4000
TIDB_USER=your_username
TIDB_PASSWORD=your_password
TIDB_DB_NAME=your_database_name

# Backend-specific Configuration
LOGFIRE_TOKEN=your_logfire_token_for_observability
```

### Development vs Production Settings
- Debug mode enabled by default in development
- API host set to 0.0.0.0 for container compatibility
- SSL certificate paths auto-detected for TiDB connections
- Logfire observability optional but recommended for production

## Key Files Reference

1. `app/main.py` - FastAPI application entry point with middleware and lifespan management
2. `app/api/v1/chat.py` - Primary API endpoints with streaming support
3. `app/services/chat_service.py` - Chat business logic with TiMemory integration
4. `app/core/config.py` - Configuration management inheriting from TiMemory
5. `app/dependencies/auth.py` - Authentication and user validation
6. `app/middleware/exception_handler.py` - Comprehensive error handling
7. `app/schemas/chat.py` - API request/response data structures
8. `app/db/database.py` - Database connection and table management

## Deployment Considerations

### Production Deployment
- Use environment variables for all sensitive configuration
- Configure proper SSL/TLS certificates for TiDB connections
- Set up Logfire or similar observability platform
- Use process managers (PM2, systemd) for service management
- Configure reverse proxy (nginx) for static file serving and SSL termination
- Set up health check endpoints for load balancer integration

### Docker Deployment
- Dockerfile included for containerized deployment
- Multi-stage build for optimized production images
- Environment variable injection for configuration
- Volume mounting for development with hot reload
- Integration with docker-compose for full stack deployment

The backend is designed as a production-ready API service with comprehensive error handling, observability, and direct integration with the TiMemory core system for advanced conversational AI capabilities.