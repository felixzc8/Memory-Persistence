# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Then edit with your values
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Running the Application
```bash
# Terminal 1: Start backend (from backend directory)
python run.py
# Alternative: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start frontend (from frontend directory)
npm run dev
```

### Frontend Development Commands
```bash
# Development server (from frontend directory)
npm run dev          # Starts Vite dev server on http://localhost:5173

# Production build
npm run build        # Builds for production
npm run preview      # Preview production build locally
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

This is a **full-stack application** with a FastAPI backend and React frontend for an AI chatbot with persistent memory capabilities.

### Core Technologies
**Backend:**
- **FastAPI** + **Uvicorn**: Web framework and ASGI server
- **OpenAI** (GPT-4o-mini default): Language model integration
- **Mem0**: Persistent memory management framework
- **TiDB Serverless**: Primary database (MySQL-compatible)
- **TiDB Vector**: Vector database for memory storage via LangChain
- **LangChain**: Vector store abstraction layer

**Frontend:**
- **React** 18: UI library
- **Vite**: Build tool and development server
- **CSS**: Terminal-styled interface (MacOS Terminal aesthetic)
- **LocalStorage**: Username persistence

### Directory Structure
```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app initialization and routes
│   │   ├── config.py            # Settings management with Pydantic
│   │   ├── api/chat.py          # Chat endpoints (/api/v1/chat, /api/v1/memories/*)
│   │   ├── services/
│   │   │   ├── chat_service.py  # OpenAI integration
│   │   │   └── memory_service.py # Mem0 memory operations
│   │   └── schemas/chat.py      # Pydantic models for request/response
│   ├── requirements.txt
│   └── run.py
└── frontend/
    ├── src/
    │   ├── App.jsx              # Main React component with chat interface
    │   ├── App.css              # Terminal styling
    │   └── main.jsx             # React entry point
    ├── index.html               # Vite HTML template
    ├── vite.config.js           # Vite configuration with API proxy
    └── package.json
```

### Application Flow
1. **Frontend**: Terminal-style React interface on `http://localhost:5173`
2. **Backend**: FastAPI server on `http://localhost:8000`
3. **Proxy**: Vite proxies `/api/*` requests to backend
4. **Authentication**: Simple username-based (no passwords)
5. **Memory**: Per-user conversation history stored in TiDB Vector

## Key Implementation Details

### Frontend Architecture
- **Single-page app** with username login screen and chat interface
- **Terminal aesthetic**: MacOS Terminal styling with monospace fonts
- **State management**: React hooks for messages, user state, and loading
- **LocalStorage persistence**: Username saved across browser sessions
- **Real-time focus management**: Input field stays focused during conversations
- **Auto-scroll**: Messages automatically scroll to bottom

### Backend Architecture
- **Clean Architecture**: API → Service → External integrations
- **Memory isolation**: Each user_id gets separate memory context
- **Error handling**: Comprehensive error responses for frontend
- **CORS enabled**: For frontend development

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
**Chat Endpoints:**
- `POST /api/v1/chat/{user_id}/new` - Create new session and send first message
- `POST /api/v1/chat/{user_id}/{session_id}` - Continue conversation in existing session
- `POST /api/v1/chat/{user_id}/new/stream` - Streaming version of new session endpoint (SSE)
- `POST /api/v1/chat/{user_id}/{session_id}/stream` - Streaming version for existing sessions (SSE)

**Session Management:**
- `GET /api/v1/chat/{user_id}/sessions` - Get list of user's sessions
- `GET /api/v1/chat/{user_id}/sessions/{session_id}` - Get specific session
- `PUT /api/v1/chat/{user_id}/sessions/{session_id}` - Update session metadata
- `DELETE /api/v1/chat/{user_id}/sessions/{session_id}` - Delete session

**Memory Management:**
- `POST /api/v1/chat/{user_id}/memories/search` - Search user memories  
- `GET /api/v1/chat/{user_id}/memories/summary` - Conversation summary
- `DELETE /api/v1/chat/{user_id}/memories` - Delete user memories

**Health Checks:**
- `GET /health` and `GET /api/v1/chat/health` - Health checks

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

## Frontend State Management

### Key React State
- `username`: Current user's display name
- `userId`: Used for backend API calls (same as username)
- `showChat`: Controls login screen vs chat interface transition
- `messages`: Array of chat messages with timestamps
- `isLoading`: Prevents duplicate requests and shows loading state

### LocalStorage Integration
- Username automatically saved on first login
- Users bypass login screen on subsequent visits
- Signout button clears localStorage and returns to login

### Focus Management
- Input field automatically focused when loading state changes
- Users can type continuously without clicking back into input
- useEffect-based approach for clean focus management

### Streaming Implementation
**Server-Sent Events (SSE):**
- Real-time streaming responses using FastAPI StreamingResponse
- EventSource API integration on frontend for SSE consumption
- Graceful fallback to regular API calls if streaming fails
- Character-by-character response rendering with typing indicators

**SSE Event Types:**
- `session_created` - New session information
- `memories_loaded` - Memory context loaded
- `content` - Streaming response chunks
- `complete` - Response finished with metadata
- `error` - Error information

## Current Status
- Full-stack application with React frontend and FastAPI backend
- Terminal-style UI with MacOS aesthetic
- Username-based authentication with localStorage persistence
- Real-time chat with persistent memory via TiDB Vector
- **NEW**: Streaming chat responses with Server-Sent Events (SSE)
- **NEW**: Real-time character-by-character response rendering
- No test suite or CI/CD pipeline currently implemented