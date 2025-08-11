import React, { useState } from 'react';
import { useApiLog } from '../contexts/ApiLogContext';
import '../styles/insight.css';

const InsightPanel = ({ username }) => {
  const { logs, isPanelOpen, clearLogs, togglePanel } = useApiLog();
  const [selectedLog, setSelectedLog] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [memories, setMemories] = useState([]);
  const [isLoadingMemories, setIsLoadingMemories] = useState(false);
  const [activeView, setActiveView] = useState('logs'); // 'logs' or 'memories'

  const formatTimestamp = (timestamp) => {
    return timestamp.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      fractionalSecondDigits: 3
    });
  };

  const formatJson = (obj) => {
    try {
      return JSON.stringify(obj, null, 2);
    } catch (e) {
      return String(obj);
    }
  };

  const getStatusColor = (status) => {
    if (status === 'pending') return '#F35048';
    if (status >= 200 && status < 300) return '#50DBD9';
    if (status >= 400) return '#DC150B';
    return '#cccccc';
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'request': return '#509DEA';
      case 'response': return '#50DBD9';
      case 'error': return '#DC150B';
      default: return '#cccccc';
    }
  };

  const fetchMemories = async () => {
    if (!username) return;
    
    setIsLoadingMemories(true);
    try {
      const response = await fetch(`/api/v1/chat/${username}/memories`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setMemories(data.memories || []);
      setActiveView('memories');
    } catch (error) {
      console.error('Error fetching memories:', error);
      setMemories([]);
    } finally {
      setIsLoadingMemories(false);
    }
  };

  const filteredLogs = logs.filter(log => 
    filterType === 'all' || log.type === filterType
  );

  if (!isPanelOpen) return null;

  return (
    <div className="insight-panel">
      <div className="insight-header">
        <div className="insight-title">Insights Panel</div>
        <div className="insight-controls">
          <button 
            onClick={() => setActiveView('logs')} 
            className={`view-toggle-btn ${activeView === 'logs' ? 'active' : ''}`}
          >
            API Logs
          </button>
          <button 
            onClick={fetchMemories} 
            className={`view-toggle-btn ${activeView === 'memories' ? 'active' : ''}`}
            disabled={isLoadingMemories || !username}
          >
            {isLoadingMemories ? 'Loading...' : 'Memories'}
          </button>
          <button onClick={togglePanel} className="close-btn">×</button>
        </div>
      </div>
      
      <div className="insight-content">
        {activeView === 'memories' ? (
          <div className="memories-list">
            <div className="memories-header">
              <h3>User Memories ({memories.length})</h3>
            </div>
            {memories.length === 0 ? (
              <div className="no-memories">No memories found for this user</div>
            ) : (
              memories.map((memory, index) => (
                <div key={memory.id || index} className="memory-entry">
                  <div className="memory-content">{memory.content}</div>
                  <div className="memory-meta">
                    <span className="memory-type">{memory.memory_attributes?.type || 'Unknown'}</span>
                    <span className="memory-status">{memory.memory_attributes?.status || 'active'}</span>
                    {memory.created_at && (
                      <span className="memory-date">
                        {new Date(memory.created_at).toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="logs-view">
            <div className="logs-controls">
              <select 
                value={filterType} 
                onChange={(e) => setFilterType(e.target.value)}
                className="filter-select"
              >
                <option value="all">All</option>
                <option value="request">Requests</option>
                <option value="response">Responses</option>
                <option value="error">Errors</option>
              </select>
              <button onClick={clearLogs} className="clear-btn">Clear</button>
            </div>
            <div className="insight-list">
              {filteredLogs.length === 0 ? (
                <div className="no-logs">No API logs to display</div>
              ) : (
                filteredLogs.map((log) => (
                <div 
                  key={log.id} 
                  className={`log-entry ${selectedLog?.id === log.id ? 'selected' : ''}`}
                  onClick={() => setSelectedLog(log)}
                >
                  <div className="log-summary">
                    <span className="log-timestamp">[{formatTimestamp(log.timestamp)}]</span>
                    <span 
                      className="log-type" 
                      style={{ color: getTypeColor(log.type) }}
                    >
                      {log.type.toUpperCase()}
                    </span>
                    <span className="log-method">{log.method}</span>
                    <span className="log-url">{log.url}</span>
                    {log.status && (
                      <span 
                        className="log-status" 
                        style={{ color: getStatusColor(log.status) }}
                      >
                        {log.status}
                      </span>
                    )}
                    {log.duration && (
                      <span className="log-duration">{log.duration}ms</span>
                    )}
                  </div>
                </div>
                ))
              )}
            </div>
          </div>
        )}
        
        {selectedLog && activeView === 'logs' && (
          <div className="log-details">
            <div className="log-details-header">
              <span 
                className="log-type-badge" 
                style={{ backgroundColor: getTypeColor(selectedLog.type) }}
              >
                {selectedLog.type.toUpperCase()}
              </span>
              <span className="log-method-url">{selectedLog.method} {selectedLog.url}</span>
              {selectedLog.status && (
                <span 
                  className="log-status-badge"
                  style={{ color: getStatusColor(selectedLog.status) }}
                >
                  {selectedLog.status} {selectedLog.statusText}
                </span>
              )}
            </div>
            
            <div className="log-details-body">
              {selectedLog.headers && Object.keys(selectedLog.headers).length > 0 && (
                <div className="log-section">
                  <h4>Headers</h4>
                  <pre className="log-json">{formatJson(selectedLog.headers)}</pre>
                </div>
              )}
              
              {selectedLog.body && (
                <div className="log-section">
                  <h4>Body</h4>
                  <pre className="log-json">
                    {typeof selectedLog.body === 'string' 
                      ? selectedLog.body 
                      : formatJson(selectedLog.body)
                    }
                  </pre>
                </div>
              )}
              
              {selectedLog.error && (
                <div className="log-section">
                  <h4>Error</h4>
                  <pre className="log-error">{selectedLog.error}</pre>
                </div>
              )}
              
              <div className="log-meta">
                <div>Timestamp: {selectedLog.timestamp.toISOString()}</div>
                {selectedLog.duration && <div>Duration: {selectedLog.duration}ms</div>}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InsightPanel;