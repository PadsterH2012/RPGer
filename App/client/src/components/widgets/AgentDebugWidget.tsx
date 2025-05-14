import React, { useState, useEffect } from 'react';
import '../../styles/widgets/AgentDebugWidget.css';

// Define debug message type
interface DebugMessage {
  id: string;
  agent: string;
  message: string;
  level: 'info' | 'warning' | 'error' | 'success';
  timestamp: Date;
}

// Mock debug messages (would come from the server in a real implementation)
const mockDebugMessages: DebugMessage[] = [
  {
    id: '1',
    agent: 'CMA',
    message: 'Character Management Agent initialized',
    level: 'info',
    timestamp: new Date(Date.now() - 60000), // 1 minute ago
  },
  {
    id: '2',
    agent: 'NEA',
    message: 'NPC & Encounter Agent initialized',
    level: 'info',
    timestamp: new Date(Date.now() - 55000), // 55 seconds ago
  },
  {
    id: '3',
    agent: 'EEA',
    message: 'Exploration Engine Agent initialized',
    level: 'info',
    timestamp: new Date(Date.now() - 50000), // 50 seconds ago
  },
  {
    id: '4',
    agent: 'WEA',
    message: 'World & Environment Agent initialized',
    level: 'info',
    timestamp: new Date(Date.now() - 45000), // 45 seconds ago
  },
  {
    id: '5',
    agent: 'MSA',
    message: 'Magic System Agent initialized',
    level: 'info',
    timestamp: new Date(Date.now() - 40000), // 40 seconds ago
  },
  {
    id: '6',
    agent: 'CaMA',
    message: 'Campaign Manager Agent initialized',
    level: 'info',
    timestamp: new Date(Date.now() - 35000), // 35 seconds ago
  },
  {
    id: '7',
    agent: 'WEA',
    message: 'Loading environment: Forgotten Forest',
    level: 'info',
    timestamp: new Date(Date.now() - 30000), // 30 seconds ago
  },
  {
    id: '8',
    agent: 'NEA',
    message: 'Preparing random encounter table for forest environment',
    level: 'info',
    timestamp: new Date(Date.now() - 25000), // 25 seconds ago
  },
  {
    id: '9',
    agent: 'CMA',
    message: 'Character stats loaded successfully',
    level: 'success',
    timestamp: new Date(Date.now() - 20000), // 20 seconds ago
  },
  {
    id: '10',
    agent: 'MSA',
    message: 'Warning: Spell components not specified',
    level: 'warning',
    timestamp: new Date(Date.now() - 15000), // 15 seconds ago
  },
];

const AgentDebugWidget: React.FC = () => {
  const [debugMessages, setDebugMessages] = useState<DebugMessage[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [filter, setFilter] = useState<string>('all');
  
  // In a real implementation, this would use the Socket context to get real-time data
  useEffect(() => {
    setDebugMessages(mockDebugMessages);
    
    // Simulate receiving new debug messages
    const interval = setInterval(() => {
      const agents = ['CMA', 'NEA', 'EEA', 'WEA', 'MSA', 'CaMA'];
      const levels = ['info', 'warning', 'error', 'success'];
      
      const newMessage: DebugMessage = {
        id: Date.now().toString(),
        agent: agents[Math.floor(Math.random() * agents.length)],
        message: `Debug message at ${new Date().toLocaleTimeString()}`,
        level: levels[Math.floor(Math.random() * levels.length)] as any,
        timestamp: new Date(),
      };
      
      setDebugMessages(prev => [...prev, newMessage]);
    }, 20000); // Add a new debug message every 20 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  // Toggle expanded state
  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };
  
  // Clear all debug messages
  const clearDebugMessages = () => {
    setDebugMessages([]);
  };
  
  // Filter debug messages
  const filteredMessages = filter === 'all' 
    ? debugMessages 
    : debugMessages.filter(msg => msg.agent === filter || msg.level === filter);
  
  // Format timestamp
  const formatTimestamp = (date: Date): string => {
    return date.toLocaleTimeString();
  };
  
  return (
    <div className={`agent-debug-widget ${isExpanded ? 'expanded' : ''}`}>
      <div className="debug-controls">
        <button 
          className="expand-button"
          onClick={toggleExpanded}
        >
          {isExpanded ? 'Collapse' : 'Expand'}
        </button>
        
        <select 
          className="filter-select"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">All</option>
          <option value="CMA">CMA</option>
          <option value="NEA">NEA</option>
          <option value="EEA">EEA</option>
          <option value="WEA">WEA</option>
          <option value="MSA">MSA</option>
          <option value="CaMA">CaMA</option>
          <option value="info">Info</option>
          <option value="warning">Warning</option>
          <option value="error">Error</option>
          <option value="success">Success</option>
        </select>
        
        <button 
          className="clear-button"
          onClick={clearDebugMessages}
        >
          Clear
        </button>
      </div>
      
      <div className="debug-messages">
        {filteredMessages.length > 0 ? (
          filteredMessages.map(message => (
            <div key={message.id} className={`debug-message ${message.level}`}>
              <div className="debug-header">
                <span className="debug-agent">{message.agent}</span>
                <span className="debug-timestamp">{formatTimestamp(message.timestamp)}</span>
              </div>
              <div className="debug-content">{message.message}</div>
            </div>
          ))
        ) : (
          <p className="no-messages">No debug messages.</p>
        )}
      </div>
    </div>
  );
};

export default AgentDebugWidget;
