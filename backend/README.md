# Chatbot with Memory - Backend

A FastAPI backend for a persistent memory chatbot using OpenAI and Mem0.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and settings
│   ├── database.py          # Database configuration and connection
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py          # Chat endpoints
│   │   └── admin.py         # Admin endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py  # OpenAI chat logic
│   │   ├── memory_service.py # Mem0 memory management
│   │   ├── user_service.py  # User management
│   │   ├── session_service.py # Session management
│   │   └── cleanup_service.py # Cleanup operations
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── chat.py          # Chat-related Pydantic models
│   │   ├── user.py          # User-related Pydantic models
│   │   └── session.py       # Session-related Pydantic models
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # Database models
│   └── test/
│       └── memory-agent.py  # Test scripts
├── run.py                   # Application runner
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Features

- **FastAPI Framework**: Modern, fast web framework for APIs
- **Persistent Memory**: Uses Mem0 with vector database for conversation memory
- **OpenAI Integration**: Powered by OpenAI's language models
- **Session Management**: Organize conversations into sessions
- **User Authentication**: JWT-based authentication system
- **Admin Interface**: Administrative endpoints for user and session management
- **Structured Code**: Clean separation of concerns with services, schemas, and API layers
- **Error Handling**: Comprehensive error handling and logging
- **Health Checks**: Built-in health check endpoints

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout

### Chat Endpoints (🔒 Authentication Required)
- `POST /api/v1/chat/{user_id}` - Send message to chatbot
- `GET /api/v1/chat/{user_id}/sessions` - Get user's chat sessions
- `POST /api/v1/chat/{user_id}/sessions` - Create new chat session
- `DELETE /api/v1/chat/{user_id}/sessions/{session_id}` - Delete chat session

### Memory Management (🔒 Authentication Required)
- `POST /api/v1/memories/search` - Search through user memories
- `GET /api/v1/memories/summary` - Get conversation summary
- `DELETE /api/v1/memories` - Delete user memories

### Admin Endpoints (🔒 Admin Access Required)
- `GET /api/v1/admin/users` - List all users
- `GET /api/v1/admin/sessions` - List all sessions
- `DELETE /api/v1/admin/users/{user_id}` - Delete user and associated data

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

# Database Configuration
DATABASE_URL=mysql://user:password@localhost/dbname

# JWT Configuration
JWT_SECRET=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Mem0 Configuration
MEM0_CONFIG_PATH=path_to_mem0_config

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

4. Set up the database:
```bash
# Run database migrations if needed
python -c "from app.database import create_tables; create_tables()"
```

5. Run the application:
```bash
# Using the run script
python run.py

# Or directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Usage Examples

### 1. User Registration
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword"
  }'
```

### 2. User Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword"
  }'
```

### 3. Chat with Memory (Authenticated)
```bash
curl -X POST "http://localhost:8000/api/v1/chat/user123" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "Hello, I am learning Python",
    "session_id": "session456"
  }'
```

### 4. Create New Session (Authenticated)
```bash
curl -X POST "http://localhost:8000/api/v1/chat/user123/sessions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Python Learning Session"
  }'
```

### 5. Search Memories (Authenticated)
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
4. **Models Layer** (`models/`): Database models and ORM definitions
5. **Configuration** (`config.py`): Centralized settings management
6. **Database** (`database.py`): Database connection and setup

## Key Features

- **🔐 JWT Authentication**: Secure user registration, login, and session management
- **🧠 Memory Integration**: Each conversation is stored and retrieved for context using Mem0
- **📚 Session Management**: Organize conversations into separate sessions
- **👤 User Isolation**: Memories and sessions are automatically isolated per user
- **🔒 Protected Routes**: Chat and memory endpoints require authentication
- **👑 Admin Interface**: Administrative endpoints for user and session management
- **🛡️ Error Resilience**: Graceful handling of API failures
- **📊 Comprehensive Logging**: Detailed logging for debugging and monitoring
- **🔒 Type Safety**: Full type hints with Pydantic validation
- **🚀 JWT Token Support**: Access token management with configurable expiration

## Development

The project is designed for easy extension:

- Add new endpoints in `api/`
- Add business logic in `services/`
- Define new data models in `schemas/`
- Add database models in `models/`
- Configure settings in `config.py`

## Security Features

🔒 **Important Security Notes:**

1. **JWT Authentication**: All protected endpoints require valid JWT tokens
2. **User Isolation**: Users can only access their own data and sessions
3. **Password Security**: Passwords are securely hashed using bcrypt
4. **Session Management**: Sessions are tied to specific users
5. **Admin Protection**: Admin endpoints require special permissions
6. **Input Validation**: All inputs are validated using Pydantic schemas

## Database Schema

The application uses the following main entities:

- **Users**: Store user authentication and profile information
- **Sessions**: Organize conversations into manageable sessions
- **Messages**: Store individual chat messages with metadata
- **Memories**: Persistent memory storage via Mem0 integration

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest backend/test/test_memory_persistence.py

# Run with coverage
python -m pytest --cov=app
```

## Deployment

For production deployment:

1. Set `DEBUG=False` in environment variables
2. Use a production WSGI server like Gunicorn
3. Set up proper database connections
4. Configure proper logging
5. Set strong JWT secrets
6. Use HTTPS for all endpoints

## Migration from Test Code

Your original test code in `app/test/memory-agent.py` has been refactored into:
- Memory operations → `services/memory_service.py`
- Chat logic → `services/chat_service.py`  
- API interface → `api/chat.py`
- Authentication → `services/user_service.py`
- Data models → `schemas/chat.py`, `schemas/user.py`, `schemas/session.py`
- Database models → `models/user.py` 