# CLAUDE.md - Frontend

This file provides guidance to Claude Code (claude.ai/code) when working with the TiMemory frontend.

## Development Commands

### Running the Application
- `npm run dev` - Start Vite development server with hot reload (default: http://localhost:5173)
- `npm run build` - Build the application for production
- `npm run preview` - Preview the production build locally
- `npm install` - Install all dependencies from package.json

### Development Tools
- Uses Vite as build tool with React plugin
- Hot module replacement (HMR) for fast development
- Proxy configuration for backend API calls

## Architecture Overview

### Tech Stack
- **React 18** - Core UI framework with hooks
- **Vite** - Modern build tool and development server
- **CSS** - Custom stylesheets for terminal-style UI
- **Fetch API** - HTTP client for backend communication
- **LocalStorage** - Client-side user session persistence

### Project Structure

**Entry Point:**
- `src/main.jsx` - React application bootstrap and DOM rendering
- `index.html` - HTML template with Vite development integration

**Core Application:**
- `src/App.jsx` - Main application component with global styles
- `src/router/AppRouter.jsx` - Client-side routing and authentication state management

**Components (`src/components/`):**
- `Login.jsx` - Username input and authentication interface
- `Chat.jsx` - Main chat interface with streaming support and session management

**Styles (`src/styles/`):**
- `global.css` - Base application styling and theme
- `login.css` - Login screen terminal-style interface
- `chat.css` - Chat interface styling with terminal aesthetic

### Application Flow

**1. Authentication (`AppRouter.jsx`)**
- Simple username-based authentication (no JWT)
- LocalStorage persistence for user sessions
- Automatic login restoration on page refresh
- State management for login/logout flow

**Key Features:**
- `handleLogin()` - Sets user state and persists to localStorage
- `handleSignout()` - Clears user data and returns to login
- Username acts as both display name and user ID

**2. Login Interface (`Login.jsx`)**
- Terminal-style welcome screen
- Username input with Enter key support
- Auto-focus for immediate user interaction
- Trim validation to prevent empty usernames

**3. Chat Interface (`Chat.jsx`)**

**State Management:**
- `messages` - Chat message history
- `sessions` - User's conversation sessions
- `currentSessionId` - Active session identifier
- `isStreaming` - Real-time streaming state
- `streamingMessage` - Partial message during streaming

**Core Features:**

**Session Management:**
- Auto-loads user sessions on component mount
- Creates new sessions automatically if none exist
- Session switching with preserved message history
- AI-generated session titles

**Real-time Chat:**
- Server-Sent Events (SSE) for streaming responses
- Incremental message updates during AI response
- Auto-scroll to newest messages
- Loading states and visual feedback

**Message Handling:**
- Timestamp formatting for all messages
- User/assistant message differentiation
- Message persistence through sessions
- Auto-focus return after interactions

### API Integration

**Backend Communication:**
All API calls use relative URLs with Vite proxy configuration:

**Chat Endpoints:**
- `POST /api/v1/chat/${userId}/stream` - Send message and receive streaming response
- `GET /api/v1/chat/${userId}/sessions` - Fetch user sessions
- `POST /api/v1/chat/${userId}/sessions` - Create new session
- `DELETE /api/v1/chat/${userId}/sessions/${sessionId}` - Delete session

**Request Patterns:**
- Uses `fetch()` API with proper error handling
- Streaming responses via EventSource for real-time updates
- JSON payloads for message sending
- RESTful URL patterns with user/session identifiers

### Streaming Implementation

**Server-Sent Events Integration:**
```javascript
const eventSource = new EventSource(`/api/v1/chat/${userId}/stream`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: input, session_id: currentSessionId })
});
```

**Event Handling:**
- `message` events - Incremental response chunks
- `session_created` events - New session notifications
- `complete` events - End of streaming response
- `error` events - Error handling and cleanup

**Streaming State Management:**
- Real-time message building with partial content
- Visual indicators for ongoing streams
- Proper cleanup on component unmount
- Error recovery and reconnection handling

### UI/UX Design

**Terminal Aesthetic:**
- Monospace fonts and terminal-style interface
- Dark background with green/white text
- Command-line inspired interactions
- Minimal, focused design for chat experience

**Responsive Features:**
- Auto-scroll to latest messages
- Input field auto-focus management
- Keyboard navigation support
- Loading states and visual feedback

**Session Management UI:**
- Session list sidebar/dropdown
- Session creation and deletion
- Current session highlighting
- Quick session switching

### State Persistence

**LocalStorage Usage:**
- Username persistence across browser sessions
- Automatic login restoration
- Simple key-value storage pattern

**Session State:**
- Messages loaded per session from backend
- Current session ID maintained in component state
- Session list refreshed on login

### Error Handling

**Network Errors:**
- Fetch request error catching
- User-friendly error messages
- Graceful degradation for offline scenarios

**Streaming Errors:**
- EventSource error handling
- Connection retry logic
- Partial message recovery

**Input Validation:**
- Empty message prevention
- Username trimming and validation
- Session ID validation before API calls

### Development Workflow

**Adding New Features:**
1. Create components in `src/components/`
2. Add styles in `src/styles/`
3. Update routing logic in `AppRouter.jsx`
4. Implement API integration with backend
5. Add error handling and loading states

**Styling Guidelines:**
- Maintain terminal aesthetic consistency
- Use CSS custom properties for theming
- Mobile-first responsive design approach
- Accessibility considerations for keyboard navigation

**API Integration:**
- Use relative URLs for Vite proxy
- Implement proper error handling
- Add loading states for better UX
- Handle streaming responses appropriately

### Build Configuration

**Vite Configuration (`vite.config.js`):**
- React plugin for JSX support
- Development server proxy to backend (localhost:8000)
- Hot module replacement enabled
- Build optimization for production

**Proxy Setup:**
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

### Key Files to Understand

1. `src/router/AppRouter.jsx` - Authentication and routing logic
2. `src/components/Chat.jsx` - Main chat interface with streaming
3. `src/components/Login.jsx` - Authentication interface
4. `vite.config.js` - Build configuration and proxy setup
5. `src/styles/chat.css` - Chat interface styling
6. `src/styles/login.css` - Login interface styling

### Development Tips

**Local Development:**
- Ensure backend is running on port 8000
- Frontend dev server runs on port 5173 by default
- API calls are proxied automatically to backend
- Hot reload works for both components and styles

**Debugging:**
- Use browser DevTools for component inspection
- Network tab for API call monitoring
- Console for streaming event debugging
- LocalStorage inspection for user session data