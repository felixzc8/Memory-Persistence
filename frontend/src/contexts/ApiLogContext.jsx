import React, { createContext, useContext, useState, useCallback } from 'react';

const ApiLogContext = createContext();

export const useApiLog = () => {
  const context = useContext(ApiLogContext);
  if (!context) {
    throw new Error('useApiLog must be used within ApiLogProvider');
  }
  return context;
};

export const ApiLogProvider = ({ children }) => {
  const [logs, setLogs] = useState([]);
  const [isPanelOpen, setIsPanelOpen] = useState(false);

  const addLog = useCallback((logEntry) => {
    const timestamp = new Date();
    const id = `${timestamp.getTime()}-${Math.random().toString(36).substr(2, 9)}`;
    
    setLogs(prev => [{
      id,
      timestamp,
      ...logEntry
    }, ...prev].slice(0, 100)); // Keep only last 100 logs
  }, []);

  const clearLogs = useCallback(() => {
    setLogs([]);
  }, []);

  const togglePanel = useCallback(() => {
    setIsPanelOpen(prev => !prev);
  }, []);

  // Custom fetch wrapper that logs requests/responses
  const loggedFetch = useCallback(async (url, options = {}) => {
    const startTime = Date.now();
    
    // Log request
    const requestLog = {
      type: 'request',
      method: options.method || 'GET',
      url,
      headers: options.headers || {},
      body: options.body || null,
      status: 'pending'
    };
    
    addLog(requestLog);
    
    try {
      const response = await fetch(url, options);
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      // Handle response body reading
      let responseBody = null;
      const contentType = response.headers.get('content-type');
      
      // Skip body reading for streaming responses
      if (contentType && contentType.includes('text/event-stream')) {
        responseBody = '[Streaming response - body not logged]';
      } else {
        // Clone response to read body without consuming it
        const responseClone = response.clone();
        
        try {
          if (contentType && contentType.includes('application/json')) {
            responseBody = await responseClone.json();
          } else if (contentType && contentType.includes('text/')) {
            responseBody = await responseClone.text();
          }
        } catch (e) {
          // Response might not be readable
          responseBody = '[Unable to read response body]';
        }
      }
      
      // Log response
      const responseLog = {
        type: 'response',
        method: options.method || 'GET',
        url,
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        body: responseBody,
        duration
      };
      
      addLog(responseLog);
      
      return response;
    } catch (error) {
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      // Log error
      const errorLog = {
        type: 'error',
        method: options.method || 'GET',
        url,
        error: error.message,
        duration
      };
      
      addLog(errorLog);
      
      throw error;
    }
  }, [addLog]);

  const value = {
    logs,
    isPanelOpen,
    addLog,
    clearLogs,
    togglePanel,
    loggedFetch
  };

  return (
    <ApiLogContext.Provider value={value}>
      {children}
    </ApiLogContext.Provider>
  );
};