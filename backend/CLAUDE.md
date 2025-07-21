# CLAUDE.md - Backend

This file provides guidance to Claude Code (claude.ai/code) when working with the TiMemory backend.

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

## Architecture Deep Dive

### Core Memory System (`memory/`)
The heart of TiMemory is a sophisticated memory processing pipeline:

**TiMem Class (`memory/timemory.py`):**
- **Memory Extraction**: Uses `FACT_EXTRACTION_PROMPT` to identify facts from conversations
- **Similarity Search**: Finds related memories using vector embeddings
- **Memory Consolidation**: Uses `MEMORY_CONSOLIDATION_PROMPT` to merge new/existing memories
- **Vector Storage**: Stores memories with embeddings in TiDB vector database

**Key Methods:**
- `process_messages()` - Main pipeline for processing user-AI conversations
- `search()` - Vector similarity search for memory retrieval
- `_extract_memories()` - LLM-based fact extraction
- `_consolidate_memories()` - Intelligent memory merging
- `_store_memories()` - Database persistence with embeddings

**Vector Database (`memory/tidb_vector.py`):**
- Custom TiDB vector operations with SSL support
- Handles embedding storage and similarity search
- User isolation through user_id filtering

### FastAPI Application Structure

**Main App (`app/main.py`):**
- FastAPI app with Logfire instrumentation for observability
- CORS middleware for frontend integration
- Custom exception handlers for different error types
- Lifespan context manager for database initialization

**Routers (`app/routers/`):**
- `chat.py` - Chat endpoints with streaming support, session management
- `admin.py` - Administrative operations for users and sessions

**Services Layer (`app/services/`):**
- `chat_service.py` - OpenAI integration with memory context and streaming
- `memory_service.py` - TiMem wrapper with FastAPI integration
- `user_service.py` - User management and authentication
- `session_service.py` - Session creation, management, and title generation

**Key Service Features:**
- **Streaming Chat**: `chat_with_memory_stream()` provides real-time responses
- **Memory Integration**: Automatic memory processing after conversations
- **Session Management**: Automatic session creation with AI-generated titles

**Models (`app/models/`):**
- SQLAlchemy ORM models for Users, Sessions, and Messages
- Database relationships and constraints
- Timestamp tracking for all entities

**Schemas (`app/schemas/`):**
Pydantic models for data validation:
- `chat.py` - Chat messages, responses, and streaming data
- `memory.py` - Memory structures with attributes (type, status)
- `user.py` - User registration, login, and profile data
- `session.py` - Session creation and management
- `error.py` - Structured error responses

**Dependencies (`app/dependencies/`):**
FastAPI dependency injection:
- `auth.py` - User authentication guards (`get_authenticated_user`)
- `memory.py` - Memory service injection
- `session.py` - Session validation and management
- `validation.py` - Input validation helpers

**Middleware (`app/middleware/`):**
- `request_id.py` - UUID tracking for request tracing
- `exception_handler.py` - Structured error handling with different exception types

### Configuration (`app/core/config.py`)

Environment-based settings using Pydantic:
- **OpenAI**: API key, model choice (gpt-4o-mini), embedding model
- **TiDB**: Connection parameters with SSL certificate configuration
- **API**: Host, port, debug mode settings
- **Observability**: Logfire token for monitoring

**Key Configuration Properties:**
- `tidb_connection_string` - Constructs SSL-enabled connection string
- Automatic SSL certificate path detection
- Environment variable loading with .env support

### Memory Processing Pipeline

**1. Message Input**
- Receives user-AI conversation history
- Validates message structure and authentication

**2. Fact Extraction**
- Uses OpenAI with structured output (Pydantic models)
- Extracts facts categorized by type: personal, preference, activity, plan, health, professional
- Generates unique IDs for each memory

**3. Similarity Search**
- Embeds new memories using OpenAI embeddings (text-embedding-3-small)
- Searches existing memories using TiDB vector operations
- Finds related memories for consolidation

**4. Memory Consolidation**
- Uses LLM to intelligently merge new and existing memories
- Avoids duplication while preserving important information
- Updates memory status (active, outdated)

**5. Storage**
- Stores consolidated memories with vector embeddings
- Maintains user isolation through user_id partitioning
- Updates existing memories or creates new ones based on status

### Database Schema

**Core Tables:**
- `users` - User authentication and profile information
- `sessions` - Conversation sessions with metadata
- `messages` - Individual chat messages with session relationship
- `memories` (TiDB vector table) - Persistent memory storage with embeddings

**Key Relationships:**
- Users have many sessions and messages
- Sessions belong to users and contain many messages
- Memories are isolated per user with vector similarity search

### Error Handling

**Custom Exception Types:**
- `DatabaseException` - Database connection and query errors
- `ValidationException` - Input validation failures
- `ChatException` - OpenAI API and chat processing errors

**Exception Handlers:**
- Structured error responses with error codes
- Request ID tracking for debugging
- Comprehensive logging with Logfire integration

### Security Features

**Authentication:**
- Simple user ID based authentication (no JWT in current implementation)
- User isolation at database and service levels
- Automatic user creation and activity tracking

**Data Protection:**
- SSL-enabled TiDB connections with certificate verification
- User memory isolation through database partitioning
- Input validation using Pydantic schemas

## Development Workflow

**Adding New Features:**
1. Define Pydantic schemas in `app/schemas/`
2. Implement business logic in `app/services/`
3. Create API endpoints in `app/routers/`
4. Add dependency injection in `app/dependencies/`
5. Update database models if needed in `app/models/`

**Memory System Extensions:**
- Modify prompts in `memory/prompts.py`
- Extend memory attributes in schemas
- Update TiDB vector operations for new features
- Adjust consolidation logic in TiMem class

**Testing:**
- Use `uv run pytest` for running tests (when test suite is added)
- Test memory processing with sample conversations
- Validate vector search functionality
- Check streaming chat responses

## Key Files to Understand

1. `app/main.py` - Application entry point and configuration
2. `memory/timemory.py` - Core memory processing logic
3. `app/services/chat_service.py` - Chat and streaming functionality
4. `app/core/config.py` - Environment configuration
5. `memory/prompts.py` - LLM prompts for memory extraction/consolidation
6. `app/routers/chat.py` - API endpoints and request handling