import React, { useState, useEffect } from 'react';
import Login from '../components/Login';
import Chat from '../components/Chat';
import { ApiLogProvider } from '../contexts/ApiLogContext';

function AppRouter() {
  const [username, setUsername] = useState('');
  const [showChat, setShowChat] = useState(false);

  useEffect(() => {
    const savedUsername = localStorage.getItem('chatUsername');
    if (savedUsername) {
      setUsername(savedUsername);
      setShowChat(true);
    }
  }, []);

  const handleLogin = (trimmedUsername) => {
    setUsername(trimmedUsername);
    setShowChat(true);
    localStorage.setItem('chatUsername', trimmedUsername);
  };

  const handleSignout = () => {
    localStorage.removeItem('chatUsername');
    setUsername('');
    setShowChat(false);
  };

  if (!showChat) {
    return (
      <Login 
        username={username}
        setUsername={setUsername}
        onLogin={handleLogin}
      />
    );
  }

  return (
    <ApiLogProvider>
      <Chat 
        username={username}
        onSignout={handleSignout}
      />
    </ApiLogProvider>
  );
}

export default AppRouter;