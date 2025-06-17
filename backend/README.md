# Homi Chatbot Backend

A FastAPI backend for a persistent memory chatbot using OpenAI and Mem0.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and settings
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat.py          # Chat endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py  # OpenAI chat logic
│   │   └── memory_service.py # Mem0 memory management
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── chat.py          # Pydantic models for API
│   ├── models/
│   │   └── __init__.py      # Database models (if needed)
│   └── test/
│       └── memory-agent.py  # Original test code
├── run.py                   # Application runner
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Features

- **FastAPI Framework**: Modern, fast web framework for APIs
- **Persistent Memory**: Uses Mem0 with Supabase for conversation memory
- **OpenAI Integration**: Powered by OpenAI's language models
- **Structured Code**: Clean separation of concerns with services, schemas, and API layers
- **Error Handling**: Comprehensive error handling and logging
- **Health Checks**: Built-in health check endpoints

## API Endpoints

### Authentication Endpoints
- `POST /api/v1/auth/signup` - Register a new user account
- `POST /api/v1/auth/signin` - Sign in an existing user
- `POST /api/v1/auth/signout` - Sign out current user
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user information
- `PUT /api/v1/auth/me` - Update user profile
- `POST /api/v1/auth/change-password` - Change user password
- `POST /api/v1/auth/reset-password` - Send password reset email
- `GET /api/v1/auth/health` - Authentication service health check

### Chat Endpoints (🔒 Authentication Required)
- `POST /api/v1/chat` - Main chat endpoint with memory context
- `POST /api/v1/chat/stream` - Streaming chat endpoint (placeholder)

### Memory Management (🔒 Authentication Required)
- `POST /api/v1/memories/search` - Search through user memories
- `GET /api/v1/memories/summary` - Get conversation summary
- `DELETE /api/v1/memories` - Delete user memories

### System
- `GET /` - Root endpoint
- `GET /health` - Application health check
- `GET /api/v1/health` - Chat service health check

## Environment Variables

Create a `.env` file in the backend directory with:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
MODEL_CHOICE=gpt-4o-mini

# Database Configuration (Supabase)
DATABASE_URL=postgresql://your_db_connection_string
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# API Configuration (optional)
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

## Installation & Setup

1. Create and activate a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env  # Copy and edit with your values
```

4. Run the application:
```bash
# Using the run script
python run.py

# Or directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Usage Examples

### 1. User Registration
```bash
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
  }'
```

### 2. User Sign In
```bash
curl -X POST "http://localhost:8000/api/v1/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### 3. Chat with Memory (Authenticated)
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "Hello, I am learning Python"
  }'
```

### 4. Search Memories (Authenticated)
```bash
curl -X POST "http://localhost:8000/api/v1/memories/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "query": "Python learning",
    "limit": 5
  }'
```

## Architecture

The backend follows a clean architecture pattern:

1. **API Layer** (`api/`): FastAPI routes and request/response handling
2. **Service Layer** (`services/`): Business logic and external service integration
3. **Schema Layer** (`schemas/`): Pydantic models for data validation
4. **Configuration** (`config.py`): Centralized settings management

## Key Features

- **🔐 Supabase Authentication**: Secure user registration, login, and session management
- **🧠 Memory Integration**: Each conversation is stored and retrieved for context
- **👤 User Isolation**: Memories are automatically isolated per authenticated user
- **🔒 Protected Routes**: Chat and memory endpoints require authentication
- **🛡️ Error Resilience**: Graceful handling of API failures
- **📊 Comprehensive Logging**: Detailed logging for debugging and monitoring
- **🔒 Type Safety**: Full type hints with Pydantic validation
- **🚀 JWT Token Support**: Access and refresh token management

## Development

The project is designed for easy extension:

- Add new endpoints in `api/`
- Add business logic in `services/`
- Define new data models in `schemas/`
- Configure settings in `config.py`

## Authentication Security

🔒 **Important Security Notes:**

1. **All chat and memory endpoints now require authentication**
2. **User isolation is automatically enforced** - users can only access their own memories
3. **JWT tokens are used for authentication** - include `Authorization: Bearer <token>` header
4. **Supabase handles password security** - passwords are securely hashed and stored
5. **Email confirmation** may be required depending on your Supabase settings

## Migration from Test Code

Your original test code in `app/test/memory-agent.py` has been refactored into:
- Memory operations → `services/memory_service.py`
- Chat logic → `services/chat_service.py`  
- API interface → `api/chat.py`
- Authentication → `services/auth_service.py` & `api/auth.py`
- Data models → `schemas/chat.py` & `schemas/auth.py` 