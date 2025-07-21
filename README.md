# TiMemory - AI Chatbot with Persistent Memory

TiMemory is an intelligent chatbot application that uses TiDB's vector database capabilities to maintain persistent memory across conversations. Built with FastAPI backend and React frontend, it provides a seamless chat experience with intelligent memory consolidation.

## 🌟 Features

- **Persistent Memory**: Conversations are remembered and consolidated using advanced AI techniques
- **Vector Database**: Powered by TiDB for efficient similarity search and memory retrieval
- **Real-time Streaming**: Live chat responses with Server-Sent Events
- **Session Management**: Organize conversations into sessions with AI-generated titles
- **Memory Consolidation**: Intelligent merging of new and existing memories to avoid duplication
- **Terminal-style UI**: Clean, focused chat interface with retro terminal aesthetic
- **User Isolation**: Complete data separation between different users

## 🏗️ Architecture

### Backend (FastAPI)
- **Memory System**: Custom TiMemory implementation for fact extraction and consolidation
- **Vector Storage**: TiDB vector database with SSL-enabled connections
- **LLM Integration**: OpenAI GPT models for chat and memory processing
- **Streaming API**: Real-time response delivery via Server-Sent Events
- **Session Management**: Automatic session creation and organization

### Frontend (React + Vite)
- **Real-time Chat**: Streaming responses with incremental updates  
- **Session Management**: Switch between conversation sessions
- **Terminal UI**: Monospace, dark theme chat interface
- **Local Persistence**: Username storage via localStorage
- **Auto-scroll**: Smart message display with auto-focus

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- TiDB Cloud account or local TiDB instance
- OpenAI API key

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   uv install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Set up environment variables in `.env`:**
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key
   MODEL_CHOICE=gpt-4o-mini
   EMBEDDING_MODEL=text-embedding-3-small

   # TiDB Configuration
   TIDB_HOST=your_tidb_host
   TIDB_PORT=4000
   TIDB_USER=your_username
   TIDB_PASSWORD=your_password
   TIDB_DB_NAME=your_database_name

   # Optional: Observability
   LOGFIRE_TOKEN=your_logfire_token
   ```

5. **Initialize database:**
   ```bash
   uv run python -c "from app.db.database import create_tables; create_tables()"
   ```

6. **Run the backend:**
   ```bash
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser to:** `http://localhost:5173`

## 💡 How It Works

### Memory Processing Pipeline

1. **Conversation Input**: User and AI messages are processed together
2. **Fact Extraction**: AI extracts relevant facts and categorizes them (personal, preferences, activities, etc.)
3. **Similarity Search**: New memories are compared against existing ones using vector embeddings
4. **Memory Consolidation**: Related memories are intelligently merged to prevent duplication
5. **Storage**: Consolidated memories are stored in TiDB with vector embeddings for future retrieval

### Memory Types

TiMemory categorizes information into several types:
- **Personal**: Names, relationships, important dates
- **Preferences**: Likes, dislikes, specific preferences
- **Activities**: Plans, events, trips, goals  
- **Professional**: Job details, career information
- **Health**: Dietary restrictions, fitness routines
- **Miscellaneous**: Books, movies, brands, other details

## 🛠️ Development

### Project Structure
```
TiMemory/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   │   ├── api/           # API endpoints  
│   │   ├── services/      # Business logic
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── core/          # Configuration
│   ├── memory/            # TiMemory core system
│   │   ├── timemory.py   # Main memory processing
│   │   ├── tidb_vector.py # Vector database operations
│   │   └── llms/         # LLM integrations
│   └── requirements.txt   # Dependencies
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── router/       # Client routing
│   │   └── styles/       # CSS styling
│   └── package.json      # Dependencies
└── README.md             # This file
```

### Development Commands

**Backend:**
```bash
# Run development server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Install new dependencies
uv add <package_name>

# Sync environment
uv sync
```

**Frontend:**
```bash
# Start development server
npm run dev

# Build for production  
npm run build

# Preview production build
npm run preview
```

### API Endpoints

**Chat:**
- `POST /api/v1/chat/{user_id}/stream` - Send message with streaming response
- `GET /api/v1/chat/{user_id}/sessions` - Get user sessions
- `POST /api/v1/chat/{user_id}/sessions` - Create new session
- `DELETE /api/v1/chat/{user_id}/sessions/{session_id}` - Delete session

**System:**
- `GET /health` - Health check
- `GET /` - Root endpoint

## 🔧 Configuration

### TiDB Setup
1. Create a TiDB Cloud cluster or set up local TiDB
2. Enable vector search capabilities
3. Configure SSL certificates for secure connections
4. Update connection parameters in `.env`

### OpenAI Setup
1. Obtain API key from OpenAI
2. Configure model preferences (gpt-4o-mini recommended)
3. Set embedding model (text-embedding-3-small)

## 🔒 Security Features

- **SSL-enabled database connections** with certificate verification
- **User data isolation** at the database level
- **Input validation** using Pydantic schemas  
- **Comprehensive error handling** with structured responses
- **Request tracking** with unique request IDs

## 📊 Observability

TiMemory includes optional Logfire integration for:
- Request tracing and performance monitoring
- Error tracking and debugging
- Database query analysis
- API endpoint usage metrics

## 🚀 Deployment

### Production Considerations
- Use environment variables for all secrets
- Enable SSL/TLS for all connections
- Configure proper database connection pooling
- Set up monitoring and logging
- Use process managers (PM2, systemd) for backend
- Serve frontend through CDN or static hosting

### Docker Support
A Dockerfile is included in the backend directory for containerized deployments.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [TiDB](https://www.pingcap.com/tidb/) for vector database capabilities
- [OpenAI](https://openai.com/) for language model integration
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://react.dev/) and [Vite](https://vitejs.dev/) for the frontend

---

Built with ❤️ using TiDB Vector Database and OpenAI