import React, { useState } from 'react';
import { useApiLog } from '../contexts/ApiLogContext';
import '../styles/apilog.css';

const ApiLogPanel = () => {
  const { logs, isPanelOpen, clearLogs, togglePanel } = useApiLog();
  const [selectedLog, setSelectedLog] = useState(null);
  const [filterType, setFilterType] = useState('all');

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
    if (status === 'pending') return '#ffa500';
    if (status >= 200 && status < 300) return '#00ff00';
    if (status >= 400) return '#ff4444';
    return '#cccccc';
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'request': return '#00aaff';
      case 'response': return '#00ff00';
      case 'error': return '#ff4444';
      default: return '#cccccc';
    }
  };

  const filteredLogs = logs.filter(log => 
    filterType === 'all' || log.type === filterType
  );

  if (!isPanelOpen) return null;

  return (
    <div className="api-log-panel">
      <div className="api-log-header">
        <div className="api-log-title">API Request/Response Log</div>
        <div className="api-log-controls">
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
          <button onClick={togglePanel} className="close-btn">×</button>
        </div>
      </div>
      
      <div className="api-log-content">
        <div className="api-log-list">
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
        
        {selectedLog && (
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

export default ApiLogPanel;