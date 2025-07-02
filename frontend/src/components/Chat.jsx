import React, { useState, useEffect, useRef } from 'react';
import '../styles/chat.css';

function Chat({ username, userId, onSignout }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
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

  useEffect(() => {
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
  }, [username]);

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