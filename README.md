# Chatbot with Memory

A full-stack chatbot application with persistent memory capabilities, built with FastAPI backend and React frontend.

## Overview

This project implements a conversational AI chatbot that maintains persistent memory across conversations. The application remembers previous interactions, user preferences, and context to provide more personalized and contextually aware responses.

## Features

- **Persistent Memory**: Conversations are stored and retrieved for context across sessions
- **Session Management**: Organize conversations into separate sessions
- **User Authentication**: Secure user registration and login
- **Real-time Chat**: Interactive chat interface with streaming responses
- **Memory Search**: Search through conversation history and memories
- **Admin Interface**: Administrative tools for user and session management
- **RESTful API**: Clean API architecture for easy integration

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for APIs
- **Mem0**: Advanced memory management for AI applications
- **OpenAI**: GPT models for natural language processing
- **MySQL**: Database for user and session storage
- **Qdrant**: Vector database for semantic memory search
- **JWT**: Token-based authentication

### Frontend
- **React**: Modern JavaScript library for building user interfaces
- **Vite**: Fast build tool and development server
- **CSS3**: Responsive styling with modern CSS features

## Project Structure

```
memory-persistence/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── models/         # Database models
│   │   └── schemas/        # Data validation schemas
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Backend documentation
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── styles/        # CSS stylesheets
│   │   └── router/        # Application routing
│   ├── package.json       # Node.js dependencies
│   └── index.html         # Main HTML file
└── README.md              # This file
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL database
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
   DATABASE_URL=mysql://user:password@localhost/dbname
   JWT_SECRET=your_jwt_secret
   ```

5. Run the backend:
   ```bash
   python run.py
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
   npm run dev
   ```

## API Documentation

The backend provides a comprehensive REST API for managing users, sessions, and conversations. Key endpoints include:

- **Authentication**: User registration, login, and session management
- **Chat**: Send messages and receive AI responses with memory context
- **Sessions**: Create, list, and manage conversation sessions
- **Memory**: Search and manage conversation memories
- **Admin**: Administrative functions for user and session management

See the [backend README](backend/README.md) for detailed API documentation.

## Development

The project is designed for easy development and extension:

- **Backend**: Add new endpoints, services, and models following the existing patterns
- **Frontend**: Create new components and styles using React best practices
- **Database**: Modify models and schemas as needed for new features
- **Memory**: Extend memory capabilities using Mem0's flexible architecture

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).
