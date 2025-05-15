import React, { useState, useEffect, useRef } from 'react';
import { useSocket } from '../../context/SocketContext';
import '../../styles/widgets/AgentDebugWidget.css';

// Define debug message type
interface DebugMessage {
  id: string;
  agent: string;
  message: string;
  level: 'info' | 'warning' | 'error' | 'success';
  timestamp: Date;
}

// Define game state interface
interface GameState {
  agent_debug: string[];
  [key: string]: any;
}

const AgentDebugWidget: React.FC = () => {
  const { socket, isConnected } = useSocket();
  const [debugMessages, setDebugMessages] = useState<DebugMessage[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [filter, setFilter] = useState<string>('all');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Connect to socket and listen for game state updates
  useEffect(() => {
    if (socket && isConnected) {
      console.log('AgentDebugWidget: Connected to socket');

      // Request initial game state
      socket.emit('get_game_state');

      // Listen for game state updates
      const handleGameStateUpdate = (gameState: GameState) => {
        if (gameState.agent_debug && gameState.agent_debug.length > 0) {
          // Process debug messages from the server
          const newMessages = gameState.agent_debug.map((message, index) => {
            // Parse the message to extract agent and level information
            let agent = 'System';
            let level: 'info' | 'warning' | 'error' | 'success' = 'info';
            let content = message;

            // Check for agent prefixes
            if (message.includes('CMA:')) {
              agent = 'CMA';
              content = message.replace('CMA:', '').trim();
            } else if (message.includes('NEA:')) {
              agent = 'NEA';
              content = message.replace('NEA:', '').trim();
            } else if (message.includes('EEA:')) {
              agent = 'EEA';
              content = message.replace('EEA:', '').trim();
            } else if (message.includes('WEA:')) {
              agent = 'WEA';
              content = message.replace('WEA:', '').trim();
            } else if (message.includes('MSA:')) {
              agent = 'MSA';
              content = message.replace('MSA:', '').trim();
            } else if (message.includes('CaMA:')) {
              agent = 'CaMA';
              content = message.replace('CaMA:', '').trim();
            }

            // Check for level indicators
            if (message.toLowerCase().includes('error')) {
              level = 'error';
            } else if (message.toLowerCase().includes('warning')) {
              level = 'warning';
            } else if (message.toLowerCase().includes('success')) {
              level = 'success';
            }

            return {
              id: `server-${Date.now()}-${index}`,
              agent,
              message: content,
              level,
              timestamp: new Date()
            };
          });

          // Update debug messages state
          setDebugMessages(prevMessages => {
            // Create a map of existing message IDs for quick lookup
            const existingIds = new Set(prevMessages.map(msg => msg.id));

            // Filter out new messages that already exist
            const uniqueNewMessages = newMessages.filter(msg => !existingIds.has(msg.id));

            // Combine existing and new messages
            return [...prevMessages, ...uniqueNewMessages];
          });
        }
      };

      socket.on('game_state_update', handleGameStateUpdate);

      // Also listen for individual debug messages
      socket.on('debug_message', (message: string) => {
        console.log('Received debug message:', message);

        // Parse the message
        let agent = 'System';
        let level: 'info' | 'warning' | 'error' | 'success' = 'info';
        let content = message;

        // Check for agent prefixes (same logic as above)
        if (message.includes('CMA:')) {
          agent = 'CMA';
          content = message.replace('CMA:', '').trim();
        } else if (message.includes('NEA:')) {
          agent = 'NEA';
          content = message.replace('NEA:', '').trim();
        } else if (message.includes('EEA:')) {
          agent = 'EEA';
          content = message.replace('EEA:', '').trim();
        } else if (message.includes('WEA:')) {
          agent = 'WEA';
          content = message.replace('WEA:', '').trim();
        } else if (message.includes('MSA:')) {
          agent = 'MSA';
          content = message.replace('MSA:', '').trim();
        } else if (message.includes('CaMA:')) {
          agent = 'CaMA';
          content = message.replace('CaMA:', '').trim();
        }

        // Check for level indicators
        if (message.toLowerCase().includes('error')) {
          level = 'error';
        } else if (message.toLowerCase().includes('warning')) {
          level = 'warning';
        } else if (message.toLowerCase().includes('success')) {
          level = 'success';
        }

        // Add the new message
        const newMessage: DebugMessage = {
          id: `realtime-${Date.now()}`,
          agent,
          message: content,
          level,
          timestamp: new Date()
        };

        setDebugMessages(prev => [...prev, newMessage]);
      });

      // Cleanup on unmount
      return () => {
        socket.off('game_state_update', handleGameStateUpdate);
        socket.off('debug_message');
      };
    }
  }, [socket, isConnected]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [debugMessages]);

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

  // Get connection status indicator
  const connectionStatus = isConnected ? (
    <span className="connection-status connected" title="Connected to backend">●</span>
  ) : (
    <span className="connection-status disconnected" title="Disconnected from backend">●</span>
  );

  // Send a debug message to the server
  const sendDebugMessage = (message: string, agent: string = 'System', level: 'info' | 'warning' | 'error' | 'success' = 'info') => {
    if (socket && isConnected) {
      socket.emit('send_debug', {
        message,
        agent,
        level
      });
    }
  };

  // Handle debug message input
  const [debugInput, setDebugInput] = useState<string>('');
  const [debugAgent, setDebugAgent] = useState<string>('System');
  const [debugLevel, setDebugLevel] = useState<'info' | 'warning' | 'error' | 'success'>('info');

  const handleDebugSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (debugInput.trim()) {
      sendDebugMessage(debugInput, debugAgent, debugLevel);
      setDebugInput('');
    }
  };

  return (
    <div className={`agent-debug-widget ${isExpanded ? 'expanded' : ''}`}>
      <div className="debug-controls">
        <div className="debug-controls-left">
          <button
            className="expand-button"
            onClick={toggleExpanded}
          >
            {isExpanded ? 'Collapse' : 'Expand'}
          </button>
          {connectionStatus}
        </div>

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
          <option value="System">System</option>
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
          <>
            {filteredMessages.map(message => (
              <div key={message.id} className={`debug-message ${message.level}`}>
                <div className="debug-header">
                  <span className="debug-agent">{message.agent}</span>
                  <span className="debug-timestamp">{formatTimestamp(message.timestamp)}</span>
                </div>
                <div className="debug-content">{message.message}</div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        ) : (
          <div className="no-messages">
            <p>No debug messages to display.</p>
            {filter !== 'all' && (
              <p>Try changing the filter from "{filter}" to "All" to see all messages.</p>
            )}
            {!isConnected && (
              <p>Not connected to backend. Check your connection and try again.</p>
            )}
          </div>
        )}
      </div>

      {isExpanded && (
        <>
          <div className="debug-input-container">
            <form onSubmit={handleDebugSubmit}>
              <div className="debug-input-controls">
                <select
                  value={debugAgent}
                  onChange={(e) => setDebugAgent(e.target.value)}
                  className="debug-agent-select"
                >
                  <option value="System">System</option>
                  <option value="CMA">CMA</option>
                  <option value="NEA">NEA</option>
                  <option value="EEA">EEA</option>
                  <option value="WEA">WEA</option>
                  <option value="MSA">MSA</option>
                  <option value="CaMA">CaMA</option>
                </select>

                <select
                  value={debugLevel}
                  onChange={(e) => setDebugLevel(e.target.value as 'info' | 'warning' | 'error' | 'success')}
                  className="debug-level-select"
                >
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="error">Error</option>
                  <option value="success">Success</option>
                </select>
              </div>

              <div className="debug-input-row">
                <input
                  type="text"
                  value={debugInput}
                  onChange={(e) => setDebugInput(e.target.value)}
                  placeholder="Enter debug message..."
                  className="debug-input"
                />
                <button type="submit" className="debug-send-button">Send</button>
              </div>
            </form>
          </div>

          <div className="debug-footer">
            <div className="debug-stats">
              <span>Total messages: {debugMessages.length}</span>
              <span>Filtered: {filteredMessages.length}</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AgentDebugWidget;
