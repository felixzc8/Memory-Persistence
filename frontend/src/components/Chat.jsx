import React, { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import { useApiLog } from '../contexts/ApiLogContext';
import ApiLogPanel from './ApiLogPanel';
import '../styles/chat.css';

function Chat({ username, userId, onSignout }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [showSessions, setShowSessions] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const { loggedFetch, isPanelOpen, togglePanel } = useApiLog();

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

  const formatMessageContent = (content) => {
    // Configure marked options
    marked.setOptions({
      breaks: true, // Enable line breaks
      gfm: true, // Enable GitHub Flavored Markdown
    });
    
    // Convert markdown to HTML
    const html = marked(content);
    
    return { __html: html };
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!isLoading && !isStreaming && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isLoading, isStreaming]);

  useEffect(() => {
    let isCancelled = false;
    
    const initializeUser = async () => {
      if (isCancelled) return;
      
      try {
        const response = await loggedFetch(`/api/v1/chat/${userId}/sessions`);
        if (isCancelled || !response.ok) {
          if (!response.ok) {
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
          return;
        }
        
        const data = await response.json();
        if (isCancelled) return;
        
        setSessions(data.sessions);
        
        if (data.sessions.length > 0) {
          const mostRecent = data.sessions[0];
          setCurrentSessionId(mostRecent.session_id);
          await loadSessionMessages(mostRecent.session_id);
        } else {
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
        if (isCancelled) return;
        
        console.error('Error loading sessions:', error);
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
    
    if (username && userId) {
      initializeUser();
    }
    
    if (inputRef.current) {
      inputRef.current.focus();
    }
    
    return () => {
      isCancelled = true;
    };
  }, [username, userId, loggedFetch]);

  const loadUserSessions = async () => {
    try {
      const response = await loggedFetch(`/api/v1/chat/${userId}/sessions`);
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
      const response = await loggedFetch(`/api/v1/chat/${userId}/sessions/${sessionId}`);
      if (response.ok) {
        const session = await response.json();
        
        const sessionMessages = session.messages.map(msg => ({
          type: msg.role,
          content: msg.content,
          timestamp: new Date(msg.timestamp)
        }));
        
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
          setCurrentSessionId(null);
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
      console.log('Ready for new session - will be created on first message');
    } catch (error) {
      console.error('Error creating new session:', error);
    }
  };

  const sendMessageStreaming = async (messageText) => {
    const userMessage = {
      type: 'user',
      content: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsStreaming(true);
    setStreamingMessage('');

    try {
      const requestBody = {
        message: messageText,
        user_id: userId
      };

      let apiUrl;
      if (currentSessionId) {
        apiUrl = `/api/v1/chat/${userId}/${currentSessionId}`;
      } else {
        apiUrl = `/api/v1/chat/${userId}/new`;
      }

      const response = await loggedFetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullResponse = '';
      let newSessionId = null;

      const streamingMessageIndex = messages.length + 1;
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true
      }]);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        const events = buffer.split('\n\n');
        buffer = events.pop() || '';

        for (const event of events) {
          if (!event.trim()) continue;
          
          const lines = event.split('\n');
          let eventType = null;
          let data = null;

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              eventType = line.substring(7);
            } else if (line.startsWith('data: ')) {
              data = line.substring(6);
            }
          }

          if (eventType && data) {
            try {
              const parsedData = JSON.parse(data);
              
              switch (eventType) {
                case 'session_created':
                  newSessionId = parsedData.session_id;
                  setCurrentSessionId(parsedData.session_id);
                  break;
                case 'content':
                  fullResponse += parsedData.content;
                  setStreamingMessage(fullResponse);
                  setMessages(prev => prev.map((msg, index) => 
                    index === streamingMessageIndex ? 
                      { ...msg, content: fullResponse } : msg
                  ));
                  break;
                case 'complete':
                  setMessages(prev => prev.map((msg, index) => 
                    index === streamingMessageIndex ? 
                      { ...msg, isStreaming: false } : msg
                  ));
                  
                  if (parsedData.session_id && parsedData.session_id !== currentSessionId) {
                    setCurrentSessionId(parsedData.session_id);
                    loadUserSessions();
                  }
                  break;
                case 'error':
                  throw new Error(parsedData.error);
              }
            } catch (parseError) {
              console.warn('Failed to parse SSE data:', parseError);
            }
          }
        }
      }
    } catch (error) {
      const errorMessage = {
        type: 'system',
        content: `Error: ${error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsStreaming(false);
      setStreamingMessage('');
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading || isStreaming) return;

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

    const messageText = input;
    setInput('');
    
    try {
      await sendMessageStreaming(messageText);
    } catch (streamError) {
      console.warn('Streaming failed, falling back to regular API:', streamError);
      
      setIsLoading(true);
      try {
        const requestBody = {
          message: messageText,
          user_id: userId
        };

        let apiUrl;
        if (currentSessionId) {
          apiUrl = `/api/v1/chat/${userId}/${currentSessionId}`;
        } else {
          apiUrl = `/api/v1/chat/${userId}/new`;
        }

        const response = await loggedFetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.session_id && data.session_id !== currentSessionId) {
          setCurrentSessionId(data.session_id);
          loadUserSessions();
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
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className={`terminal ${isPanelOpen ? 'with-api-panel' : ''}`}>
      <ApiLogPanel />
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
              <span style={{ color: '#666666', fontSize: '12px' }}>
                [{formatTimestamp(message.timestamp)}]
              </span>
              {message.type === 'user' && (
                <span style={{ color: '#DC150B' }}> {username}$: </span>
              )}
              {message.type === 'assistant' && (
                <span style={{ color: '#cccccc' }}> assistant: </span>
              )}
              {message.type === 'system' && (
                <span style={{ color: '#888888' }}> system: </span>
              )}
              <span 
                dangerouslySetInnerHTML={formatMessageContent(message.content)}
              />
              {message.isStreaming && <span className="cursor"></span>}
            </div>
          ))}
          {isLoading && !isStreaming && (
            <div className="message loading">
              <span style={{ color: '#666666', fontSize: '12px' }}>
                [{formatTimestamp(new Date())}]
              </span>
              <span style={{ color: '#cccccc' }}> assistant: </span>
              <span>Thinking...</span>
              <span className="cursor"></span>
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
            disabled={isLoading || isStreaming}
          />
          <button 
            className="sessions-btn"
            onClick={() => setShowSessions(!showSessions)}
            title="Sessions"
          >
            sessions
          </button>
          <button 
            className="api-log-btn"
            onClick={togglePanel}
            title="Toggle API Log Panel"
          >
            log
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