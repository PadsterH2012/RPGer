import React, { useState, useEffect } from 'react';
import '../../styles/widgets/ActionResultsWidget.css';

// Define action result type
interface ActionResult {
  id: string;
  type: 'attack' | 'skill' | 'save' | 'spell' | 'other';
  description: string;
  outcome: string;
  timestamp: Date;
}

// Mock action results (would come from the server in a real implementation)
const mockActionResults: ActionResult[] = [
  {
    id: '1',
    type: 'attack',
    description: 'Longsword attack against Goblin',
    outcome: 'Hit! 8 damage dealt.',
    timestamp: new Date(Date.now() - 60000), // 1 minute ago
  },
  {
    id: '2',
    type: 'skill',
    description: 'Perception check',
    outcome: 'Success! You notice a hidden door in the north wall.',
    timestamp: new Date(Date.now() - 120000), // 2 minutes ago
  },
  {
    id: '3',
    type: 'save',
    description: 'Dexterity saving throw',
    outcome: 'Failed! You take 5 fire damage from the trap.',
    timestamp: new Date(Date.now() - 180000), // 3 minutes ago
  },
  {
    id: '4',
    type: 'spell',
    description: 'Cast Magic Missile',
    outcome: 'Success! 3 missiles hit the enemy for a total of 9 damage.',
    timestamp: new Date(Date.now() - 240000), // 4 minutes ago
  },
  {
    id: '5',
    type: 'other',
    description: 'Search the bookshelf',
    outcome: 'You find an old scroll and a small potion.',
    timestamp: new Date(Date.now() - 300000), // 5 minutes ago
  },
];

const ActionResultsWidget: React.FC = () => {
  const [actionResults, setActionResults] = useState<ActionResult[]>([]);
  
  // In a real implementation, this would use the Socket context to get real-time data
  useEffect(() => {
    setActionResults(mockActionResults);
    
    // Simulate receiving new action results
    const interval = setInterval(() => {
      const newAction: ActionResult = {
        id: Date.now().toString(),
        type: ['attack', 'skill', 'save', 'spell', 'other'][Math.floor(Math.random() * 5)] as any,
        description: 'New action performed',
        outcome: Math.random() > 0.5 ? 'Success!' : 'Failed!',
        timestamp: new Date(),
      };
      
      setActionResults(prev => [newAction, ...prev].slice(0, 10)); // Keep only the 10 most recent
    }, 30000); // Add a new action every 30 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  // Format timestamp
  const formatTimestamp = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    
    if (diffSec < 60) return `${diffSec}s ago`;
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHour < 24) return `${diffHour}h ago`;
    return date.toLocaleDateString();
  };
  
  // Get class name based on action type
  const getActionClass = (type: string): string => {
    switch (type) {
      case 'attack': return 'action-attack';
      case 'skill': return 'action-skill';
      case 'save': return 'action-save';
      case 'spell': return 'action-spell';
      default: return 'action-other';
    }
  };
  
  // Get icon based on action type
  const getActionIcon = (type: string): string => {
    switch (type) {
      case 'attack': return '⚔️';
      case 'skill': return '🔍';
      case 'save': return '🛡️';
      case 'spell': return '✨';
      default: return '📝';
    }
  };
  
  return (
    <div className="action-results-widget">
      <div className="action-results-list">
        {actionResults.length > 0 ? (
          actionResults.map(action => (
            <div key={action.id} className={`action-result ${getActionClass(action.type)}`}>
              <div className="action-icon">{getActionIcon(action.type)}</div>
              <div className="action-content">
                <div className="action-header">
                  <span className="action-description">{action.description}</span>
                  <span className="action-timestamp">{formatTimestamp(action.timestamp)}</span>
                </div>
                <div className="action-outcome">{action.outcome}</div>
              </div>
            </div>
          ))
        ) : (
          <p className="no-actions">No actions performed yet.</p>
        )}
      </div>
    </div>
  );
};

export default ActionResultsWidget;
