import React, { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import { useApiLog } from '../contexts/ApiLogContext';
import InsightPanel from './InsightPanel';
import '../styles/chat.css';

function Chat({ username, onSignout }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
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
    const initializeUser = async () => {
      try {
        const response = await loggedFetch(`/api/v1/chat/${username}/sessions`);
        if (!response.ok) {
          setMessages([
            {
              type: 'system',
              content: 'Memory Persistence Chat Terminal v2.0.0',
              timestamp: new Date()
            },
            {
              type: 'system',
              content: `Welcome ${username}! Use 'sessions' to manage conversations.`,
              timestamp: new Date()
            }
          ]);
          return;
        }
        
        const data = await response.json();
        setSessions(data.sessions);
        
        if (data.sessions.length > 0) {
          const mostRecent = data.sessions[0]; 
          setCurrentSessionId(mostRecent.session_id);
          await loadSessionMessages(mostRecent.session_id);
        } else {
          setMessages([
            {
              type: 'system',
              content: 'Memory Persistence Chat Terminal v2.0.0',
              timestamp: new Date()
            },
            {
              type: 'system',
              content: `Welcome ${username}! Use 'sessions' to manage conversations.`,
              timestamp: new Date()
            }
          ]);
        }
      } catch (error) {
        console.error('Error loading sessions:', error);
        setMessages([
          {
            type: 'system',
            content: 'Memory Persistence Chat Terminal v2.0.0',
            timestamp: new Date()
          },
          {
            type: 'system',
            content: `Welcome ${username}! Use 'sessions' to manage conversations.`,
            timestamp: new Date()
          }
        ]);
      }
    };
    
    if (username) {
      initializeUser();
    }
  }, [username, loggedFetch]);

  const loadUserSessions = async () => {
    try {
      const response = await loggedFetch(`/api/v1/chat/${username}/sessions`);
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
      const response = await loggedFetch(`/api/v1/chat/${username}/sessions/${sessionId}`);
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
          content: 'Memory Persistence Chat Terminal v2.0.0',
          timestamp: new Date()
        },
        {
          type: 'system',
          content: 'Starting new chat session...',
          timestamp: new Date()
        }
      ]);
      console.log('Ready for new session - will be created on first message');
      
      // Focus the input after creating new session
      if (inputRef.current) {
        inputRef.current.focus();
      }
    } catch (error) {
      console.error('Error creating new session:', error);
    }
  };


  const parseSSEEvent = (event) => {
    if (!event.trim()) return null;
    
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
    
    if (!eventType || !data) return null;
    
    try {
      return { eventType, parsedData: JSON.parse(data) };
    } catch (parseError) {
      console.warn('Failed to parse SSE data:', parseError);
      return null;
    }
  };

  const handleSSEEvent = (eventType, parsedData, streamingMessageIndex, fullResponseRef) => {
    switch (eventType) {
      case 'session_created':
        setCurrentSessionId(parsedData.session_id);
        break;
      case 'content':
        fullResponseRef.current += parsedData.content;
        setMessages(prev => prev.map((msg, index) => 
          index === streamingMessageIndex ? 
            { ...msg, content: fullResponseRef.current } : msg
        ));
        break;
      case 'complete':
        if (parsedData.session_id && parsedData.session_id !== currentSessionId) {
          setCurrentSessionId(parsedData.session_id);
          loadUserSessions();
        }
        if (parsedData.memories && parsedData.memories.length > 0) {
          console.log('Memories used for response:', parsedData.memories);
        }
        break;
      case 'error':
        throw new Error(parsedData.error);
    }
  };

  const processStreamChunk = (buffer, decoder, value, streamingMessageIndex, fullResponseRef) => {
    const newBuffer = buffer + decoder.decode(value, { stream: true });
    const events = newBuffer.split('\n\n');
    const remainingBuffer = events.pop() || '';
    
    for (const event of events) {
      const parsed = parseSSEEvent(event);
      if (!parsed) continue;
      
      handleSSEEvent(parsed.eventType, parsed.parsedData, streamingMessageIndex, fullResponseRef);
    }
    
    return remainingBuffer;
  };

  const sendMessageStreaming = async (messageText) => {
    const userMessage = {
      type: 'user',
      content: messageText,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsStreaming(true);

    try {
      const requestBody = { message: messageText, user_id: username };
      const url = currentSessionId 
        ? `/api/v1/chat/${username}/${currentSessionId}` 
        : `/api/v1/chat/${username}/new`;
      
      const response = await loggedFetch(url, {
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
      const streamingMessageIndex = messages.length + 1;
      const fullResponseRef = { current: '' };
      let buffer = '';
      
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: '',
        timestamp: new Date()
      }]);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        buffer = processStreamChunk(buffer, decoder, value, streamingMessageIndex, fullResponseRef);
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

    setInput('');
    
    await sendMessageStreaming(input);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && !isStreaming) {
        sendMessage();
      }
    }
  };


  return (
    <div className={`terminal ${isPanelOpen ? 'with-insight-panel' : ''}`}>
      <InsightPanel username={username} />
      {showSessions && (
        <div className="sessions-sidebar">
          <div className="sessions-header">
            <h3>Chat Sessions</h3>
            <button onClick={() => setShowSessions(false)} className="close-btn">×</button>
          </div>
          <div className="sessions-actions">
            <button onClick={() => {
              createNewSession();
            }} className="new-session-btn">+ New Chat</button>
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
            </div>
          ))}
          {isLoading && !isStreaming && (
            <div className="message loading">
              <span style={{ color: '#666666', fontSize: '12px' }}>
                [{formatTimestamp(new Date())}]
              </span>
              <span style={{ color: '#cccccc' }}> assistant: </span>
              <span>Thinking...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <div className="input-container">
          <span className="prompt">{username}$:</span>
          <textarea
            ref={inputRef}
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={false}
            rows={1}
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