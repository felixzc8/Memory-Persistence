import React, { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState('');
  const [username, setUsername] = useState('');
  const [showChat, setShowChat] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const usernameInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!isLoading && showChat && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isLoading, showChat]);

  useEffect(() => {
    const savedUsername = localStorage.getItem('chatUsername');
    if (savedUsername) {
      setUsername(savedUsername);
      setUserId(savedUsername);
      setShowChat(true);
    }
  }, []);

  useEffect(() => {
    if (showChat) {
      setMessages([
        {
          type: 'system',
          content: `Memory Persistence Chat Terminal v1.0.0`,
          timestamp: new Date()
        },
        {
          type: 'system',
          content: `Welcome ${username}! Connected to backend. Type your message and press Enter.`,
          timestamp: new Date()
        }
      ]);
      
      if (inputRef.current) {
        inputRef.current.focus();
      }
    } else {
      if (usernameInputRef.current) {
        usernameInputRef.current.focus();
      }
    }
  }, [showChat, username]);

  const handleUsernameSubmit = () => {
    if (!username.trim()) return;
    
    const trimmedUsername = username.trim();
    setUserId(trimmedUsername);
    setShowChat(true);
    localStorage.setItem('chatUsername', trimmedUsername);
  };

  const handleUsernameKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleUsernameSubmit();
    }
  };

  const handleSignout = () => {
    localStorage.removeItem('chatUsername');
    setUsername('');
    setUserId('');
    setShowChat(false);
    setMessages([]);
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          user_id: userId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
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

  const formatTimestamp = (timestamp) => {
    return timestamp.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  if (!showChat) {
    return (
      <div className="terminal">
        <div className="start-screen">
          <div className="welcome-text">
            <h1>Memory Persistence Chat Terminal</h1>
            <p>Enter your username to begin</p>
          </div>
          <div className="username-input-container">
            <span className="prompt">username:</span>
            <input
              ref={usernameInputRef}
              type="text"
              className="username-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyPress={handleUsernameKeyPress}
              placeholder="Enter username..."
            />
            <span className="cursor">|</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="terminal">
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
            placeholder="Type your message..."
            disabled={isLoading}
          />
          {!isLoading && <span className="cursor">|</span>}
          <button 
            className="signout-btn"
            onClick={handleSignout}
            title="Sign out"
          >
            exit
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;