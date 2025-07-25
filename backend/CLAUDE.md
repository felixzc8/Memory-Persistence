# CLAUDE.md - Backend

This file provides guidance to Claude Code (claude.ai/code) when working with the FastAPI backend.

## Development Commands

### Running the Application
- `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` - Start development server with hot reload
- `uv run python app/main.py` - Run the app directly using the built-in uvicorn launcher
- `uv install` - Install all dependencies from pyproject.toml and create/update uv.lock
- `uv sync` - Sync the virtual environment with the lock file

### Development Tools
- `uv run python -c "from app.db.database import create_tables; create_tables()"` - Initialize database tables
- `uv run python fix_schema.py` - Run schema fixes if needed
- `uv add <package>` - Add new dependencies
- `uv remove <package>` - Remove dependencies

## API Documentation

### Chat Endpoints (`/api/v1/chat`)

**POST** `/{user_id}/new` - Create new chat session
- Creates new session and processes first message
- **Content Negotiation**: 
  - `Accept: application/json` → Returns `ChatResponse` JSON object
  - `Accept: text/event-stream` → Returns streaming response via Server-Sent Events

```bash
# JSON response
curl -X POST "http://localhost:8000/api/v1/chat/user123/new" \
  -H "Content-Type: application/json" \
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
  -H "Accept: text/event-stream" \
  -d '{"message": "Tell me a story", "user_id": "user123"}'

# Response (Server-Sent Events):
event: session_created
data: {"session_id": "uuid-string", "title": "Tell me a story"}

event: content
data: {"content": "Once"}

event: content
data: {"content": " upon a time..."}
```

**POST** `/{user_id}/{session_id}` - Continue existing chat session

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
- Returns: Success confirmation message

```bash
# Delete session
curl -X DELETE "http://localhost:8000/api/v1/chat/user123/sessions/session-uuid-123"

# Response:
{
  "message": "Session deleted successfully"
}
```

**POST** `/{user_id}/memories/search` - Search user memories

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

```bash
# Delete all user memories
curl -X DELETE "http://localhost:8000/api/v1/chat/user123/memories"

# Response:
{
  "message": "Memories deleted for user user123"
}
```

**GET** `/health` - Service health check

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

### Admin Endpoints (`/api/v1/admin`)
- Currently minimal structure for future administrative functions

## FastAPI Application Architecture

### Main Application (`app/main.py`)
- **FastAPI App**: Configured with title, description, version
- **Middleware Stack**:
  - `RequestIDMiddleware` - UUID tracking for request correlation
  - `CORSMiddleware` - Frontend integration with full CORS support
- **Exception Handlers**: Custom handlers for different error types
- **Observability**: Logfire integration for monitoring and logging
- **Lifespan Management**: Database table creation on startup

### Services Layer (`app/services/`)

**Chat Service (`chat_service.py`)**:
- `chat_with_memory()` - Standard chat with memory context integration
- `chat_with_memory_stream()` - Streaming chat responses using SSE
- `get_conversation_summary()` - AI-generated conversation summaries
- OpenAI integration with configurable models

**Memory Service (`memory_service.py`)**:
- TiMemory system wrapper for FastAPI integration
- Vector search capabilities for user memories
- Memory deletion and management operations

**User Service (`user_service.py`)**:
- User authentication and validation
- Database health checking
- User activity tracking

**Session Service (`session_service.py`)**:
- Session creation with AI-generated titles
- Session metadata management (update, delete)
- User session listing and retrieval

### Data Models

**Pydantic Schemas (`app/schemas/`)**:
- `ChatRequest` / `ChatResponse` - Chat message structures
- `MemorySearchRequest` / `MemorySearchResponse` - Memory search operations
- `Session` / `SessionListResponse` / `UpdateSessionRequest` - Session management
- `User` - User profile and authentication data
- Error response models for structured API errors

**SQLAlchemy Models (`app/models/`)**:
- `User` - User accounts with timestamps
- `Session` - Chat sessions with metadata and user relationships
- `Message` - Individual chat messages linked to sessions
- `Memory` - Vector-enabled memory storage (TiDB specific)

### Dependencies (`app/dependencies/`)

**Authentication (`auth.py`)**:
- `get_authenticated_user()` - User ID validation
- Simple authentication system (no JWT currently)

**Session Management (`session.py`)**:
- `get_user_session()` - Session ownership verification
- Session existence and access validation

**Validation (`validation.py`)**:
- `validate_chat_request()` - Chat input validation
- `validate_memory_search_request()` - Search input validation

**Memory Integration (`memory.py`)**:
- `get_available_memory_service()` - Memory service dependency injection

### Middleware (`app/middleware/`)

**Request ID Tracking (`request_id.py`)**:
- Generates UUID for each request
- Enables request correlation across logs
- Adds request ID to response headers

**Exception Handling (`exception_handler.py`)**:
- `DatabaseException` - Database connectivity and query errors
- `ValidationException` - Input validation failures  
- `ChatException` - LLM and chat processing errors
- `HTTPException` - Standard HTTP errors
- Structured error responses with error codes and request IDs

### Configuration (`app/core/config.py`)

**Environment Settings**:
- **OpenAI Configuration**: API key, model selection (gpt-4o-mini), embeddings
- **TiDB Settings**: Host, port, credentials, SSL configuration
- **API Settings**: Host (0.0.0.0), port (8000), debug mode
- **Observability**: Logfire token for monitoring

**Key Properties**:
- `tidb_connection_string` - SSL-enabled database connection
- Automatic SSL certificate detection
- `.env` file support for local development

### Database Integration (`app/db/`)

**Database Connection (`database.py`)**:
- SQLAlchemy engine configuration
- SSL-enabled TiDB connections
- Automatic table creation utilities
- Connection pooling and management

## Development Workflow

### Adding New API Endpoints
1. Define request/response schemas in `app/schemas/`
2. Implement business logic in appropriate service (`app/services/`)
3. Create API endpoint in `app/api/v1/`
4. Add authentication/validation dependencies
5. Consider content negotiation if multiple response types needed
6. Update documentation and error handling

### Extending Memory Functionality
1. Update memory schemas for new fields/operations
2. Extend memory service methods
3. Add new API endpoints for memory operations
4. Test vector search and storage functionality

### Error Handling Best Practices
- Use appropriate custom exception types
- Include request IDs in error responses
- Log errors with structured data for observability
- Provide meaningful error messages for API consumers

### Security Considerations
- All chat endpoints require user authentication
- Session endpoints validate user ownership
- Memory operations are user-isolated
- SSL-enabled database connections
- Input validation on all endpoints

## Key Files Reference

1. `app/main.py` - Application entry point and configuration
2. `app/api/v1/chat.py` - Primary API endpoints and routing
3. `app/services/chat_service.py` - Chat logic with streaming support
4. `app/core/config.py` - Environment and database configuration
5. `app/dependencies/auth.py` - Authentication and user validation
6. `app/middleware/exception_handler.py` - Error handling and responses
7. `app/schemas/chat.py` - API request/response data structures