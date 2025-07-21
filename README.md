# AI Chatbot with Persistent Memory

A full-stack AI chatbot application with persistent memory capabilities, built with FastAPI backend and React frontend. The system maintains conversation context across sessions using advanced memory management.

## Overview

This project implements a conversational AI chatbot that maintains persistent memory across conversations using TiDB Vector database. The application remembers previous interactions, user preferences, and context to provide more personalized and contextually aware responses with a terminal-style interface.

## Features

- **Persistent Memory**: Conversation history stored in TiDB Vector database for context retrieval
- **Session Management**: Organize conversations into separate sessions per user
- **Simple Authentication**: Username-based login with localStorage persistence
- **Real-time Chat**: Interactive terminal-style chat interface with streaming responses
- **Memory Search**: Search through conversation history and memories
- **Streaming Responses**: Server-Sent Events (SSE) for real-time character-by-character responses
- **Terminal UI**: MacOS Terminal-inspired aesthetic with monospace fonts
- **RESTful API**: Clean API architecture for easy integration

## Technology Stack

### Backend
- **FastAPI** + **Uvicorn**: Modern web framework and ASGI server
- **Mem0**: Advanced memory management for AI applications
- **OpenAI**: GPT models (GPT-4o-mini default) for natural language processing
- **TiDB Serverless**: MySQL-compatible primary database
- **TiDB Vector**: Vector database for semantic memory storage
- **LangChain**: Vector store abstraction layer

### Frontend
- **React** 18: Modern JavaScript library for building user interfaces
- **Vite**: Fast build tool and development server
- **CSS**: Terminal-styled interface with MacOS aesthetic
- **LocalStorage**: Username persistence across browser sessions

## Project Structure

```
memory-persistence/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── main.py         # FastAPI app initialization and routes
│   │   ├── config.py       # Settings management with Pydantic
│   │   ├── api/chat.py     # Chat endpoints (/api/v1/chat, /api/v1/memories/*)
│   │   ├── services/
│   │   │   ├── chat_service.py  # OpenAI integration
│   │   │   └── memory_service.py # Mem0 memory operations
│   │   └── schemas/chat.py # Pydantic models for request/response
│   ├── requirements.txt    # Python dependencies
│   └── run.py             # Application entry point
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── App.jsx        # Main React component with chat interface
│   │   ├── App.css        # Terminal styling
│   │   └── main.jsx       # React entry point
│   ├── index.html         # Vite HTML template
│   ├── vite.config.js     # Vite configuration with API proxy
│   └── package.json       # Node.js dependencies
├── CLAUDE.md              # Claude Code development instructions
└── README.md              # This file
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- TiDB Serverless database (or MySQL-compatible)
- OpenAI API key

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create `.env` file):
   ```env
   OPENAI_API_KEY=your_openai_api_key
   MODEL_CHOICE=gpt-4o-mini
   TIDB_HOST=your_tidb_host
   TIDB_PORT=4000
   TIDB_USER=your_tidb_user
   TIDB_PASSWORD=your_tidb_password
   TIDB_DB_NAME=your_database_name
   ```

5. Run the backend:
   ```bash
   python run.py
   # Alternative: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev    # Starts on http://localhost:5173
   ```

### Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## API Documentation

The backend provides a comprehensive REST API for chat functionality with persistent memory:

### Chat Endpoints
- `POST /api/v1/chat/{user_id}/new` - Create new session and send first message
- `POST /api/v1/chat/{user_id}/{session_id}` - Continue conversation in existing session
- `POST /api/v1/chat/{user_id}/new/stream` - Streaming version of new session endpoint (SSE)
- `POST /api/v1/chat/{user_id}/{session_id}/stream` - Streaming version for existing sessions (SSE)

### Session Management
- `GET /api/v1/chat/{user_id}/sessions` - Get list of user's sessions
- `GET /api/v1/chat/{user_id}/sessions/{session_id}` - Get specific session
- `PUT /api/v1/chat/{user_id}/sessions/{session_id}` - Update session metadata
- `DELETE /api/v1/chat/{user_id}/sessions/{session_id}` - Delete session

### Memory Management
- `POST /api/v1/chat/{user_id}/memories/search` - Search user memories
- `GET /api/v1/chat/{user_id}/memories/summary` - Conversation summary
- `DELETE /api/v1/chat/{user_id}/memories` - Delete user memories

### Health Checks
- `GET /health` and `GET /api/v1/chat/health` - Health checks

See the FastAPI auto-generated documentation at http://localhost:8000/docs for detailed API specifications.

## Key Features

### Memory Management
- Uses Mem0 with automatic user isolation via user_id
- Memories stored in TiDB Vector database via LangChain integration
- Each conversation maintains context through memory retrieval
- Vector table name: `memory_vectors` (configurable)

### Streaming Implementation
- Server-Sent Events (SSE) for real-time streaming responses
- EventSource API integration on frontend for SSE consumption
- Character-by-character response rendering with typing indicators
- Graceful fallback to regular API calls if streaming fails

### Frontend Architecture
- Single-page app with username login screen and chat interface
- Terminal aesthetic with MacOS Terminal styling and monospace fonts
- State management using React hooks for messages, user state, and loading
- LocalStorage persistence for username across browser sessions
- Real-time focus management and auto-scroll functionality

### Backend Architecture
- Clean Architecture: API → Service → External integrations
- Memory isolation: Each user_id gets separate memory context
- Comprehensive error handling and CORS enabled for development
- TiDB Serverless with SSL connection for database operations

## Development

The project follows clean architecture principles:

- **Backend**: FastAPI with service layer architecture and Pydantic validation
- **Frontend**: React with hooks-based state management and CSS styling
- **Database**: TiDB Vector for memory storage with cosine similarity search
- **Memory**: Mem0 framework with LangChain integration for vector operations

### Testing Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Chat endpoint (requires proper TiDB/OpenAI configuration)
curl -X POST "http://localhost:8000/api/v1/chat/test_user/new" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).
