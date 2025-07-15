import React, { useState, useEffect, useRef } from 'react';
import '../styles/chat.css';

function Chat({ username, userId, onSignout }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [showSessions, setShowSessions] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTimestamp = (timestamp) => {
    return timestamp.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!isLoading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isLoading]);

  // Load user sessions on mount
  useEffect(() => {
    const initializeUser = async () => {
      try {
        const response = await fetch(`/api/v1/chat/${userId}/sessions`);
        if (response.ok) {
          const data = await response.json();
          setSessions(data.sessions);
          
          // If user has sessions, load the most recent one
          if (data.sessions.length > 0) {
            const mostRecent = data.sessions[0]; // Already sorted by last_activity
            setCurrentSessionId(mostRecent.session_id);
            await loadSessionMessages(mostRecent.session_id);
          } else {
            // Only set default welcome messages if no sessions exist
            setMessages([
              {
                type: 'system',
                content: `Memory Persistence Chat Terminal v2.0.0`,
                timestamp: new Date()
              },
              {
                type: 'system',
                content: `Welcome ${username}! Connected to backend. Use 'sessions' to manage conversations.`,
                timestamp: new Date()
              }
            ]);
          }
        } else {
          // Fallback to default messages if API fails
          setMessages([
            {
              type: 'system',
              content: `Memory Persistence Chat Terminal v2.0.0`,
              timestamp: new Date()
            },
            {
              type: 'system',
              content: `Welcome ${username}! Connected to backend. Use 'sessions' to manage conversations.`,
              timestamp: new Date()
            }
          ]);
        }
      } catch (error) {
        console.error('Error loading sessions:', error);
        // Fallback to default messages
        setMessages([
          {
            type: 'system',
            content: `Memory Persistence Chat Terminal v2.0.0`,
            timestamp: new Date()
          },
          {
            type: 'system',
            content: `Welcome ${username}! Connected to backend. Use 'sessions' to manage conversations.`,
            timestamp: new Date()
          }
        ]);
      }
    };
    
    initializeUser();
    
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, [username]);

  const loadUserSessions = async () => {
    try {
      const response = await fetch(`/api/v1/chat/${userId}/sessions`);
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const loadSessionMessages = async (sessionId) => {
    try {
      const response = await fetch(`/api/v1/chat/${userId}/sessions/${sessionId}`);
      if (response.ok) {
        const session = await response.json();
        
        // Convert session messages to chat format
        const sessionMessages = session.messages.map(msg => ({
          type: msg.role,
          content: msg.content,
          timestamp: new Date(msg.timestamp)
        }));
        
        // Add system messages and session messages
        setMessages([
          {
            type: 'system',
            content: `Memory Persistence Chat Terminal v2.0.0`,
            timestamp: new Date()
          },
          {
            type: 'system',
            content: `Loaded session: ${session.title}`,
            timestamp: new Date()
          },
          ...sessionMessages
        ]);
      }
    } catch (error) {
      console.error('Error loading session messages:', error);
    }
  };

  const createNewSession = async () => {
    try {
      // Reset current session state
      setCurrentSessionId(null);
      
      // Reset messages for new session
      setMessages([
        {
          type: 'system',
          content: `Memory Persistence Chat Terminal v2.0.0`,
          timestamp: new Date()
        },
        {
          type: 'system',
          content: `Starting new chat session...`,
          timestamp: new Date()
        }
      ]);
      
      // Session will be created automatically when first message is sent
      console.log('Ready for new session - will be created on first message');
    } catch (error) {
      console.error('Error creating new session:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    // Handle special commands
    if (input.trim() === 'sessions') {
      setShowSessions(!showSessions);
      setInput('');
      return;
    }

    if (input.trim() === 'new') {
      createNewSession();
      setInput('');
      return;
    }

    const userMessage = {
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const requestBody = {
        message: input,
        user_id: userId
      };

      let apiUrl;
      if (currentSessionId) {
        // Continue existing session
        apiUrl = `/api/v1/chat/${userId}/${currentSessionId}`;
      } else {
        // Create new session
        apiUrl = `/api/v1/chat/${userId}/new`;
      }

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Update current session ID if a new one was created
      if (data.session_id && data.session_id !== currentSessionId) {
        setCurrentSessionId(data.session_id);
        loadUserSessions(); // Refresh sessions list
      }
      
      const assistantMessage = {
        type: 'assistant',
        content: data.response || 'No response received',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        type: 'system',
        content: `Error: ${error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="terminal">
      {showSessions && (
        <div className="sessions-sidebar">
          <div className="sessions-header">
            <h3>Chat Sessions</h3>
            <button onClick={() => setShowSessions(false)} className="close-btn">×</button>
          </div>
          <div className="sessions-actions">
            <button onClick={createNewSession} className="new-session-btn">+ New Chat</button>
          </div>
          <div className="sessions-list">
            {sessions.map((session) => (
              <div 
                key={session.session_id} 
                className={`session-item ${session.session_id === currentSessionId ? 'active' : ''}`}
                onClick={() => {
                  setCurrentSessionId(session.session_id);
                  loadSessionMessages(session.session_id);
                  setShowSessions(false);
                }}
              >
                <div className="session-title">{session.title}</div>
                <div className="session-meta">
                  {session.message_count} messages • {new Date(session.last_activity).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="terminal-body">
        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message message-${message.type}`}>
              <span style={{ color: '#666', fontSize: '12px' }}>
                [{formatTimestamp(message.timestamp)}]
              </span>
              {message.type === 'user' && (
                <span style={{ color: '#00ff00' }}> {username}$: </span>
              )}
              {message.type === 'assistant' && (
                <span style={{ color: '#27ca3f' }}> assistant: </span>
              )}
              {message.type === 'system' && (
                <span style={{ color: '#ffbd2e' }}> system: </span>
              )}
              <span>{message.content}</span>
            </div>
          ))}
          {isLoading && (
            <div className="message loading">
              <span style={{ color: '#666', fontSize: '12px' }}>
                [{formatTimestamp(new Date())}]
              </span>
              <span style={{ color: '#27ca3f' }}> assistant: </span>
              <span>Thinking...</span>
              <span className="cursor">|</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <div className="input-container">
          <span className="prompt">{username}$:</span>
          <input
            ref={inputRef}
            type="text"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type message, 'sessions', or 'new'..."
            disabled={isLoading}
          />
          {!isLoading && <span className="cursor">|</span>}
          <button 
            className="sessions-btn"
            onClick={() => setShowSessions(!showSessions)}
            title="Sessions"
          >
            sessions
          </button>
          <button 
            className="signout-btn"
            onClick={onSignout}
            title="Sign out"
          >
            exit
          </button>
        </div>
      </div>
    </div>
  );
}

export default Chat;