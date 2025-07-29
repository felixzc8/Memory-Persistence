# CLAUDE.md - Frontend

This file provides guidance to Claude Code (claude.ai/code) when working with the TiMemory React frontend.

## Development Commands

### Running the Application
- `npm run dev` - Start Vite development server with hot reload (default: http://localhost:5173)
- `npm run build` - Build the application for production with optimized bundles
- `npm run preview` - Preview the production build locally
- `npm install` - Install all dependencies from package.json

### Development Tools
- **Vite**: Modern build tool with React plugin for fast development and HMR
- **Hot Module Replacement (HMR)**: Live updates without full page reload
- **API Proxy**: Automatic proxy configuration for backend API calls
- **Development Server**: Optimized for React development with fast builds

## Project Structure

### Tech Stack
- **React 18**: Core UI framework with hooks and modern patterns
- **Vite**: Next-generation build tool for fast development and optimized production builds
- **Marked**: Markdown parsing library for rendering AI responses with formatting
- **CSS**: Custom stylesheets implementing terminal-style design
- **Fetch API**: Modern HTTP client for backend communication with streaming support
- **LocalStorage**: Client-side user session persistence

### Application Architecture

**Entry Point:**
- `src/main.jsx` - React application bootstrap with React 18 createRoot and DOM rendering
- `index.html` - HTML template with Vite development integration and meta configuration

**Core Application:**
- `src/App.jsx` - Main application component with global styling and router integration
- `src/router/AppRouter.jsx` - Client-side routing and authentication state management

**Components (`src/components/`):**
- `Login.jsx` - Username-based authentication interface with terminal styling
- `Chat.jsx` - Main chat interface with streaming support, session management, and markdown rendering
- `ApiLogPanel.jsx` - Development debugging panel for API request/response monitoring

**Contexts (`src/contexts/`):**
- `ApiLogContext.jsx` - React context for API logging and debugging functionality

**Styles (`src/styles/`):**
- `global.css` - Base application styling, typography, and color scheme
- `login.css` - Login screen terminal-style interface with focus effects
- `chat.css` - Chat interface styling with terminal aesthetic and responsive design
- `apilog.css` - API debugging panel styling for development workflow

### Application Flow

**1. Authentication System (`AppRouter.jsx`)**
The application uses a simple but effective authentication system:

- **Username-based Authentication**: No complex JWT or OAuth, just username storage
- **LocalStorage Persistence**: User sessions persist across browser restarts
- **Automatic Login Restoration**: Seamless experience on page refresh
- **State Management**: React hooks for login/logout flow management

**Key Features:**
- `handleLogin()` - Sets user state and persists to localStorage for session continuity
- `handleSignout()` - Clears user data and returns to clean login state
- Username validation with trimming to prevent empty or whitespace-only usernames
- Graceful handling of localStorage errors and edge cases

**2. Login Interface (`Login.jsx`)**
Terminal-inspired authentication experience:

- **Terminal Welcome Screen**: ASCII-style branding and instructions
- **Username Input**: Single field with Enter key support for quick interaction
- **Auto-focus**: Immediate cursor placement for seamless user experience
- **Input Validation**: Trim whitespace and prevent empty submissions
- **Terminal Aesthetic**: Monospace fonts, green text, and retro computing feel

**3. Chat Interface (`Chat.jsx`)**

**State Management:**
The chat component maintains comprehensive state for real-time interaction:

- `messages` - Complete chat message history with role-based organization
- `sessions` - User's conversation sessions with metadata and quick switching
- `currentSessionId` - Active session identifier for message routing
- `isStreaming` - Real-time streaming state for UI feedback
- `streamingMessage` - Partial message content during AI response streaming
- `isLoading` - Loading states for user feedback during operations

**Core Chat Features:**

**Real-time Streaming Chat:**
- **Server-Sent Events (SSE)**: Live streaming of AI responses with incremental updates
- **EventSource Integration**: Robust connection handling with automatic error recovery
- **Streaming Message Building**: Real-time assembly of AI responses character by character
- **Visual Streaming Indicators**: User feedback during active streaming
- **Proper Connection Cleanup**: Memory leak prevention and resource management

**Session Management:**
- **Auto-session Creation**: Automatic session creation if no sessions exist
- **Session Switching**: Quick navigation between different conversation contexts
- **AI-generated Titles**: Intelligent session naming based on conversation content
- **Session Metadata**: Tracking of creation time, activity, and message counts
- **Session Persistence**: Server-side storage with client-side caching

**Message Handling:**
- **Markdown Rendering**: Full markdown support with GitHub Flavored Markdown using `marked` library
- **Timestamp Formatting**: Precise time display for all messages with 24-hour format
- **Role-based Display**: Visual differentiation between user and assistant messages
- **Message Persistence**: Server-side storage with optimistic UI updates
- **Auto-scroll Behavior**: Smart scrolling to newest messages with smooth animations

**Advanced UI Features:**
- **Auto-focus Management**: Input field focus returns after all interactions
- **Session Dropdown**: Collapsible session list with hover effects and visual feedback
- **Loading States**: Comprehensive loading indicators for all async operations
- **Error Handling**: Graceful degradation with user-friendly error messages
- **Responsive Design**: Mobile-first approach with terminal aesthetic preservation

### API Integration

**Backend Communication:**
All API calls utilize relative URLs with Vite's built-in proxy configuration:

**Chat Endpoints:**
- `POST /api/v1/chat/${userId}/new` - Create new session with streaming response support
- `POST /api/v1/chat/${userId}/${sessionId}` - Continue existing session with memory context
- `GET /api/v1/chat/${userId}/sessions` - Fetch user sessions with metadata
- `DELETE /api/v1/chat/${userId}/sessions/${sessionId}` - Delete session and cleanup

**Request Patterns:**
- **Fetch API**: Modern promise-based HTTP client with comprehensive error handling
- **Streaming Responses**: EventSource for real-time Server-Sent Events integration
- **JSON Payloads**: Structured request/response format with proper content types
- **RESTful Design**: Intuitive URL patterns with user/session resource identifiers
- **Error Propagation**: Structured error handling with user feedback

### Streaming Implementation

**Server-Sent Events Integration:**
The frontend implements sophisticated streaming for real-time chat experience:

```javascript
// Streaming endpoint with proper error handling
const response = await loggedFetch(`/api/v1/chat/${username}/${currentSessionId}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'text/event-stream'
  },
  body: JSON.stringify({ message: input, user_id: username })
});

// EventSource for streaming data
const eventSource = new EventSource(response.url);
```

**Event Handling:**
- `content` events - Incremental response chunks for real-time display
- `session_created` events - New session notifications with metadata
- `complete` events - End of streaming response with cleanup
- `error` events - Error handling and connection recovery

**Streaming State Management:**
- **Real-time Message Building**: Progressive assembly of AI responses with partial content display
- **Visual Streaming Indicators**: Loading states and visual feedback during active streams
- **Proper Resource Cleanup**: EventSource connection management and memory leak prevention
- **Error Recovery**: Automatic reconnection and fallback to non-streaming mode
- **Connection Monitoring**: Health checks and connection status tracking

### UI/UX Design Philosophy

**Terminal Aesthetic Implementation:**
The entire interface embraces a retro terminal computing aesthetic:

- **Typography**: Monospace fonts (JetBrains Mono, Consolas) for authentic terminal feel
- **Color Scheme**: Dark background (#0a0a0a) with green (#00ff00) and white (#ffffff) text
- **Visual Elements**: Cursor effects, text shadows, and glow effects for retro appeal
- **Interaction Design**: Command-line inspired user interactions and feedback

**Responsive Design Principles:**
- **Mobile-first Approach**: Optimized for mobile devices while maintaining desktop functionality
- **Flexible Layouts**: CSS Grid and Flexbox for adaptive layouts across screen sizes
- **Touch-friendly**: Adequate touch targets and gesture support for mobile users
- **Performance Optimization**: Efficient rendering and minimal resource usage

**User Experience Features:**
- **Auto-scroll Behavior**: Intelligent scrolling to latest messages with smooth animations
- **Input Field Management**: Auto-focus after interactions for seamless typing experience
- **Loading State Feedback**: Visual indicators for all async operations and data loading
- **Keyboard Navigation**: Full keyboard accessibility and navigation support
- **Error User Feedback**: User-friendly error messages with actionable suggestions

### State Persistence Strategy

**LocalStorage Usage:**
The application implements strategic client-side persistence:

- **Username Persistence**: Automatic login restoration across browser sessions
- **Simple Key-value Storage**: Straightforward localStorage implementation without complex serialization
- **Error Handling**: Graceful fallback for localStorage unavailability or quota exceeded scenarios
- **Privacy Considerations**: Only essential data stored locally with user control

**Session State Management:**
- **Server-side Authority**: All session data managed on backend for consistency
- **Client-side Caching**: Session list cached for improved performance and offline browsing
- **Optimistic Updates**: Immediate UI updates with server synchronization
- **Conflict Resolution**: Server state takes precedence over client state

### Error Handling and Resilience

**Network Error Management:**
- **Fetch Request Error Catching**: Comprehensive error handling for all API calls
- **User-friendly Error Messages**: Technical errors translated to actionable user feedback
- **Graceful Degradation**: Functional core features maintained during network issues
- **Retry Logic**: Automatic retry for transient network failures

**Streaming Error Handling:**
- **EventSource Error Management**: Robust error handling for streaming connections
- **Connection Recovery**: Automatic reconnection with exponential backoff
- **Fallback Mechanisms**: Non-streaming mode fallback for compatibility
- **Partial Message Recovery**: Preservation of partially received messages

**UI Error States:**
- **Loading State Management**: Clear visual feedback for all async operations
- **Input Validation**: Client-side validation with user-friendly feedback
- **Session Management Errors**: Graceful handling of session creation and deletion failures
- **Accessibility**: Error messages compatible with screen readers and assistive technologies

### Development Workflow

**Adding New UI Components:**
1. Create component in `src/components/` following React hooks patterns
2. Add corresponding styles in `src/styles/` maintaining terminal aesthetic
3. Update routing logic in `AppRouter.jsx` if navigation changes required
4. Implement API integration with proper error handling and loading states
5. Add real-time features using streaming where applicable
6. Test across different screen sizes and interaction methods

**Extending Chat Functionality:**
1. Update chat component state management for new features
2. Implement streaming integration for real-time features
3. Add API endpoints integration with backend services
4. Update UI components with appropriate visual feedback
5. Test streaming functionality with various connection scenarios
6. Ensure mobile responsiveness and accessibility compliance

**Styling Guidelines:**
- **Consistency**: Maintain terminal aesthetic across all components
- **CSS Custom Properties**: Use CSS variables for theming and consistency
- **Mobile-first**: Responsive design starting with mobile constraints
- **Performance**: Efficient CSS with minimal runtime calculations
- **Accessibility**: Color contrast, keyboard navigation, screen reader support

### Build Configuration

**Vite Configuration (`vite.config.js`):**
- **React Plugin**: @vitejs/plugin-react for JSX support and Fast Refresh
- **Development Server**: Hot module replacement with proxy configuration
- **Build Optimization**: Tree shaking, code splitting, and asset optimization for production
- **Environment Variables**: Support for VITE_BACKEND_URL configuration

**API Proxy Setup:**
```javascript
server: {
  proxy: {
    '/api': {
      target: process.env.VITE_BACKEND_URL || 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

**Production Build Features:**
- **Code Splitting**: Automatic chunking for optimal loading performance
- **Asset Optimization**: Image compression, CSS minification, and JS optimization
- **Modern JS Output**: ES2020+ with fallbacks for broader browser support
- **Bundle Analysis**: Built-in tools for analyzing bundle size and dependencies

### API Logging and Debugging

**Development Debugging (`ApiLogPanel.jsx`):**
- **Request/Response Logging**: Complete API interaction logging for development
- **Real-time Monitoring**: Live display of API calls with timing information
- **Error Tracking**: Detailed error logging with stack traces and context
- **Performance Metrics**: Request timing and response size tracking

**ApiLogContext Integration:**
- **Context Provider**: React context for sharing API logging across components
- **Intercepted Fetch**: Wrapper around fetch API for automatic logging
- **Toggle Functionality**: Show/hide debugging panel for clean development
- **Export Capabilities**: Save API logs for debugging and analysis

### Performance Optimizations

**React Performance:**
- **Hooks Optimization**: Proper dependency arrays and memoization where beneficial
- **Component Re-render Prevention**: Strategic use of React.memo and useCallback
- **State Update Batching**: Efficient state updates to minimize re-renders
- **Virtual Scrolling**: Efficient message rendering for long conversation histories

**Network Performance:**
- **Request Batching**: Combine related API calls where possible
- **Caching Strategy**: Intelligent caching of session data and user preferences
- **Connection Reuse**: HTTP/2 connection pooling for reduced latency
- **Compression**: Request/response compression for reduced bandwidth usage

**Asset Loading:**
- **Lazy Loading**: Components and assets loaded on demand
- **Code Splitting**: Route-based and component-based code splitting
- **Asset Optimization**: Image compression and efficient asset delivery
- **Caching Headers**: Proper cache control for static assets

### Environment Configuration

**Environment Variables:**
- `VITE_BACKEND_URL` - Backend API URL (defaults to http://localhost:8000)
- Development/production configuration via Vite's environment system
- Build-time variable injection for configuration management

**Development vs Production:**
- **Development**: Hot reload, API proxy, debugging panels, verbose logging
- **Production**: Optimized bundles, minified assets, error tracking, performance monitoring

### Key Files Reference

1. `src/router/AppRouter.jsx` - Authentication flow and routing logic with session management
2. `src/components/Chat.jsx` - Main chat interface with streaming and session management
3. `src/components/Login.jsx` - Authentication interface with terminal styling
4. `src/contexts/ApiLogContext.jsx` - API logging context for development debugging
5. `vite.config.js` - Build configuration, proxy setup, and development server settings
6. `src/styles/chat.css` - Chat interface styling with terminal aesthetic and responsive design
7. `src/styles/login.css` - Login interface styling with focus effects and terminal theme

### Browser Compatibility

**Modern Browser Support:**
- **ES2020+ Features**: Native modules, async/await, destructuring, optional chaining
- **Fetch API**: Modern HTTP client with streaming support
- **EventSource**: Server-Sent Events for real-time streaming
- **LocalStorage**: Client-side persistence with graceful fallbacks
- **CSS Grid/Flexbox**: Modern layout systems with fallbacks

**Progressive Enhancement:**
- **Core Functionality**: Basic chat works without advanced features
- **Streaming Fallback**: Non-streaming mode for incompatible browsers/networks
- **Offline Capabilities**: Basic functionality maintained during network issues
- **Accessibility**: Full screen reader and keyboard navigation support

### Deployment Considerations

**Production Build:**
- **Static Asset Generation**: All assets bundled and optimized for CDN delivery
- **Environment Configuration**: Production API endpoints and configuration
- **Error Boundary**: Production error handling and user feedback
- **Performance Monitoring**: Integration with monitoring services for production insights

**CDN Deployment:**
- **Static Hosting**: Compatible with Netlify, Vercel, AWS S3, CloudFront
- **Single Page Application**: Proper routing configuration for SPA hosting
- **Asset Caching**: Optimal cache headers for performance
- **Compression**: Gzip/Brotli compression for reduced load times

**Docker Integration:**
- **Multi-stage Build**: Optimized Docker images with build and runtime stages
- **Nginx Serving**: Production-ready static file serving with proxy configuration
- **Environment Injection**: Runtime environment variable configuration
- **Health Checks**: Container health monitoring for orchestration platforms

The frontend is designed as a modern, responsive React application with real-time streaming capabilities, comprehensive error handling, and a unique terminal aesthetic that provides an engaging user experience while maintaining professional functionality.