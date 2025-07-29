# TiMemory - AI Chatbot with Persistent Memory

TiMemory is an advanced AI chatbot system that maintains persistent, contextual memory across conversations using TiDB's vector database capabilities. The system features intelligent memory extraction, consolidation, and retrieval, providing users with a truly personalized conversational experience.

## 🌟 Key Features

- **Persistent Memory System**: Advanced AI-powered memory extraction and consolidation using vector embeddings
- **Real-time Streaming**: Live chat responses via Server-Sent Events with incremental message updates
- **Session Management**: Organize conversations into sessions with AI-generated titles
- **Memory Consolidation**: Intelligent merging and conflict resolution for memories to prevent duplication
- **Vector Database**: TiDB-powered similarity search for contextual memory retrieval
- **Terminal-style Interface**: Clean, focused chat UI with retro terminal aesthetics
- **User Isolation**: Complete data separation and privacy between users
- **Memory Forgetting**: Human-like memory updates that preserve context rather than deleting information

## 🏗️ System Architecture

### Core TiMemory Engine (`TiMemory/`)
The heart of the system is a sophisticated memory processing pipeline:

1. **Memory Extraction**: AI-powered fact extraction from conversations with semantic categorization
2. **Similarity Search**: Vector-based matching against existing memories using 1536-dimensional embeddings
3. **Memory Consolidation**: LLM-driven conflict resolution and intelligent memory merging
4. **Vector Storage**: Persistent storage in TiDB with user isolation and temporal tracking

**Memory Categories:**
- Personal (relationships, important dates)
- Preferences (likes, dislikes, opinions)
- Activities (events, plans, behaviors)
- Professional (career, work details)
- Health (dietary restrictions, fitness)
- Miscellaneous (entertainment, interests)

### FastAPI Backend (`backend/`)
- **API Layer**: RESTful endpoints with FastAPI, comprehensive error handling
- **Services Layer**: Business logic for chat, memory, user, and session management
- **Memory Integration**: TiMemory system wrapper for web API integration
- **Authentication**: Simple username-based authentication with user data isolation
- **Middleware**: Request ID tracking, CORS handling, structured exception responses
- **Observability**: Logfire integration for monitoring, logging, and performance tracking

### React Frontend (`frontend/`)
- **Real-time Chat**: Streaming chat interface with Server-Sent Events
- **Session Management**: Create, switch, and delete conversation sessions
- **Terminal UI**: Monospace, dark-themed interface optimized for chat
- **Local Persistence**: Username storage via localStorage
- **Auto-scroll & Focus**: Smart UX with automatic message scrolling and input focus

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ with `uv` package manager
- Node.js 16+ with npm
- TiDB Cloud account or local TiDB instance with vector search enabled
- OpenAI API key

### Backend Setup

1. **Install TiMemory core system:**
   ```bash
   cd TiMemory
   uv install
   ```

2. **Configure TiMemory environment:**
   ```bash
   cp .env.example .env
   # Edit .env with TiDB and OpenAI credentials
   ```

3. **Setup and run backend:**
   ```bash
   cd ../backend
   uv install
   cp .env.example .env
   # Edit .env with your configuration
   
   # Initialize database tables
   uv run python -c "from app.db.database import create_tables; create_tables()"
   
   # Start development server
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. **Install and run frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

2. **Access the application:** `http://localhost:5173`

### Docker Deployment

```bash
# Run the entire stack
docker-compose up --build

# Access frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

## 🛠️ Development

### Project Structure
```
TiMemory/
├── TiMemory/                    # Core memory engine (separate package)
│   ├── timemory.py             # Main memory processing pipeline
│   ├── tidb_vector.py          # Vector database operations
│   ├── models/                 # Data models (Memory, Session, etc.)
│   ├── embedding/              # OpenAI embedding integration
│   ├── llms/                   # LLM wrappers and integrations
│   ├── config/                 # Configuration management
│   └── MEMORY.md               # Detailed technical documentation
├── backend/                     # FastAPI web application
│   ├── app/
│   │   ├── api/v1/             # API endpoints (chat, admin)
│   │   ├── services/           # Business logic layer
│   │   ├── models/             # SQLAlchemy database models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── dependencies/       # FastAPI dependency injection
│   │   ├── middleware/         # Request processing middleware
│   │   ├── core/               # Configuration and exceptions
│   │   └── db/                 # Database connection management
│   └── CLAUDE.md               # Backend development guide
├── frontend/                    # React application
│   ├── src/
│   │   ├── components/         # React components (Chat, Login, etc.)
│   │   ├── contexts/           # React context providers
│   │   ├── router/             # Client-side routing
│   │   └── styles/             # CSS styling
│   └── CLAUDE.md               # Frontend development guide
└── docker-compose.yml          # Multi-service deployment
```

### Development Commands

**TiMemory Core:**
```bash
cd TiMemory
uv run python -c "from timemory import TiMemory; # test core functionality"
```

**Backend:**
```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload  # Dev server
uv run python app/main.py                                        # Direct run
uv add <package>                                                  # Add dependency
uv sync                                                           # Sync environment
```

**Frontend:**
```bash
cd frontend
npm run dev      # Development server (http://localhost:5173)
npm run build    # Production build
npm run preview  # Preview production build
```

## 🔧 Configuration

### Environment Variables

**Core TiMemory (`.env` in TiMemory/):**
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

# Memory System Settings
MEMORY_COLLECTION_NAME=memories
MEMORY_SEARCH_LIMIT=10
MESSAGE_LIMIT=20
SUMMARY_THRESHOLD=10
```

**Backend API (`.env` in backend/):**
```env
# Inherits TiMemory config plus:
LOGFIRE_TOKEN=your_logfire_token_for_observability
```

### TiDB Setup
1. Create TiDB Cloud cluster with vector search enabled
2. Configure SSL certificates for secure connections
3. Create database and enable vector operations
4. Update connection parameters in environment files

## 💡 How TiMemory Works

### Memory Processing Pipeline

1. **Conversation Analysis**: User-AI message pairs are analyzed for factual content
2. **Memory Extraction**: AI extracts structured facts and categorizes them by type
3. **Similarity Search**: New memories are compared against existing ones using vector embeddings
4. **Consolidation**: Related memories are intelligently merged, with conflicts resolved through LLM reasoning
5. **Storage**: Consolidated memories are stored with vector embeddings for future similarity search

### Advanced Memory Features

**Memory Forgetting vs. Deletion:**
- Memories are marked as "outdated" rather than deleted
- Preserves context for understanding preference changes
- Enables nuanced AI responses based on memory evolution
- Maintains audit trail of user interactions

**Cross-Referential Inference:**
- Extracts implied facts from multi-turn conversations
- Handles complex references to previous assistant responses  
- Infers preferences from contextual cues and behavioral patterns
- Resolves temporal references and implicit connections

## 📊 API Reference

### Chat Endpoints (`/api/v1/chat`)

**POST `/{user_id}/new`** - Create new chat session
- Content negotiation: JSON response or streaming via Server-Sent Events
- Creates session with AI-generated title
- Processes first message with memory context

**POST `/{user_id}/{session_id}`** - Continue existing session
- Streams AI responses with memory integration
- Updates conversation context and extracts new memories

**GET `/{user_id}/sessions`** - List user's chat sessions
**GET `/{user_id}/sessions/{session_id}`** - Get specific session details
**PUT `/{user_id}/sessions/{session_id}`** - Update session metadata
**DELETE `/{user_id}/sessions/{session_id}`** - Delete session and messages

**Memory Operations:**
- **POST `/{user_id}/memories/search`** - Search user memories by query
- **GET `/{user_id}/memories/summary`** - Get AI-generated memory summary
- **DELETE `/{user_id}/memories`** - Clear all user memories

**GET `/health`** - System health check with component status

## 🔒 Security & Privacy

- **SSL-enabled database connections** with certificate verification
- **User data isolation** at database level with indexed partitioning
- **Input validation** using Pydantic schemas across all endpoints
- **Comprehensive error handling** with sanitized responses
- **Request tracking** with UUID correlation across services
- **Memory attribution** with immutable user associations

## 📈 Performance & Scalability

**Optimization Features:**
- Vector indexing for O(log n) similarity search
- Connection pooling for database efficiency
- Deferred loading of vector columns in search results
- User-isolated queries with B-tree indexing
- Batch embedding generation for cost efficiency

**Resource Usage:**
- ~$0.00002 per 1K tokens for embeddings (OpenAI pricing)
- ~$0.00015 per 1K tokens for LLM processing (gpt-4o-mini)
- ~1KB per memory + 6KB vector storage in database
- ~10MB vector index overhead per 1K memories

## 🚀 Deployment

### Production Considerations
- Use environment variables for all secrets and configuration
- Enable SSL/TLS for all external connections
- Configure proper database connection pooling and timeouts
- Set up monitoring with Logfire or similar observability platform
- Use process managers (PM2, systemd) for backend service management
- Serve frontend through CDN or optimized static hosting

### Docker Deployment
```bash
# Multi-service deployment
docker-compose up --build

# Individual services
docker build -t timemory-backend ./backend
docker build -t timemory-frontend ./frontend
```

## 📚 Documentation

- **`TiMemory/MEMORY.md`** - Detailed technical architecture documentation
- **`backend/CLAUDE.md`** - Backend API development guide with examples
- **`frontend/CLAUDE.md`** - Frontend development guide and component architecture

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes with appropriate tests
4. Update documentation as needed
5. Submit pull request with detailed description

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **[TiDB](https://www.pingcap.com/tidb/)** - Vector database and distributed SQL capabilities
- **[OpenAI](https://openai.com/)** - Language models and embedding services
- **[FastAPI](https://fastapi.tiangolo.com/)** - High-performance Python web framework
- **[React](https://react.dev/) & [Vite](https://vitejs.dev/)** - Modern frontend development tools
- **[Logfire](https://logfire.pydantic.dev/)** - Python-native observability platform

---

**Built with ❤️ using TiDB Vector Database, OpenAI, and modern web technologies**