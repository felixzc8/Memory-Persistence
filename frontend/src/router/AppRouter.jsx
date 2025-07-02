import React, { useState, useEffect, useRef } from 'react';
import Login from '../components/Login';
import Chat from '../components/Chat';

function AppRouter() {
  const [userId, setUserId] = useState('');
  const [username, setUsername] = useState('');
  const [showChat, setShowChat] = useState(false);
  const usernameInputRef = useRef(null);

  useEffect(() => {
    const savedUsername = localStorage.getItem('chatUsername');
    if (savedUsername) {
      setUsername(savedUsername);
      setUserId(savedUsername);
      setShowChat(true);
    }
  }, []);

  const handleLogin = (trimmedUsername) => {
    setUserId(trimmedUsername);
    setUsername(trimmedUsername);
    setShowChat(true);
    localStorage.setItem('chatUsername', trimmedUsername);
  };

  const handleSignout = () => {
    localStorage.removeItem('chatUsername');
    setUsername('');
    setUserId('');
    setShowChat(false);
  };

  if (!showChat) {
    return (
      <Login 
        username={username}
        setUsername={setUsername}
        onLogin={handleLogin}
        usernameInputRef={usernameInputRef}
      />
    );
  }

  return (
    <Chat 
      username={username}
      userId={userId}
      onSignout={handleSignout}
    />
  );
}

export default AppRouter;