import React, { useEffect } from 'react';
import '../styles/login.css';

function Login({ username, setUsername, onLogin, usernameInputRef }) {
  useEffect(() => {
    if (usernameInputRef.current) {
      usernameInputRef.current.focus();
    }
  }, [usernameInputRef]);

  const handleUsernameSubmit = () => {
    if (!username.trim()) return;
    onLogin(username.trim());
  };

  const handleUsernameKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleUsernameSubmit();
    }
  };

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
        </div>
      </div>
    </div>
  );
}

export default Login;