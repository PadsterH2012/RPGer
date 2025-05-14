import React, { useState, useEffect, useRef } from 'react';
import '../../styles/widgets/DungeonMasterWidget.css';

// Define DM message type
interface DMMessage {
  id: string;
  content: string;
  timestamp: Date;
  isVisible: boolean;
}

// Mock DM messages (would come from the server in a real implementation)
const mockInitialMessages: DMMessage[] = [
  {
    id: '1',
    content: 'Welcome to the Forgotten Forest. The path ahead splits in two directions. To the left, you see a narrow trail leading deeper into the woods. To the right, there's a wider path that seems more traveled.',
    timestamp: new Date(),
    isVisible: true,
  },
  {
    id: '2',
    content: 'You hear rustling in the bushes nearby. Something or someone is watching you.',
    timestamp: new Date(Date.now() - 30000), // 30 seconds ago
    isVisible: true,
  },
];

const DungeonMasterWidget: React.FC = () => {
  const [messages, setMessages] = useState<DMMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // In a real implementation, this would use the Socket context to get real-time data
  useEffect(() => {
    setMessages(mockInitialMessages);
    
    // Simulate receiving new DM messages
    const interval = setInterval(() => {
      const newMessage: DMMessage = {
        id: Date.now().toString(),
        content: 'The forest grows darker as time passes. You should consider your next move carefully.',
        timestamp: new Date(),
        isVisible: true,
      };
      
      // Add new message and keep only the last 2 visible
      setMessages(prev => {
        const updatedMessages = [...prev, newMessage];
        // If we have more than 2 messages, mark older ones as not visible
        if (updatedMessages.length > 2) {
          const visibleCount = updatedMessages.filter(m => m.isVisible).length;
          if (visibleCount > 2) {
            // Find the oldest visible message and mark it as not visible
            const oldestVisibleIndex = updatedMessages.findIndex(m => m.isVisible);
            if (oldestVisibleIndex !== -1) {
              updatedMessages[oldestVisibleIndex] = {
                ...updatedMessages[oldestVisibleIndex],
                isVisible: false,
              };
            }
          }
        }
        return updatedMessages;
      });
    }, 60000); // Add a new message every minute
    
    return () => clearInterval(interval);
  }, []);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };
  
  // Handle form submit
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() === '') return;
    
    // In a real implementation, this would send the message to the server
    // For now, we'll just add it to the messages array
    const playerMessage: DMMessage = {
      id: `player-${Date.now()}`,
      content: `Player: ${inputValue}`,
      timestamp: new Date(),
      isVisible: true,
    };
    
    setMessages(prev => {
      const updatedMessages = [...prev, playerMessage];
      // If we have more than 2 messages, mark older ones as not visible
      if (updatedMessages.length > 2) {
        const visibleCount = updatedMessages.filter(m => m.isVisible).length;
        if (visibleCount > 2) {
          // Find the oldest visible message and mark it as not visible
          const oldestVisibleIndex = updatedMessages.findIndex(m => m.isVisible);
          if (oldestVisibleIndex !== -1) {
            updatedMessages[oldestVisibleIndex] = {
              ...updatedMessages[oldestVisibleIndex],
              isVisible: false,
            };
          }
        }
      }
      return updatedMessages;
    });
    
    // Clear input
    setInputValue('');
    
    // Simulate DM response
    setTimeout(() => {
      const dmResponse: DMMessage = {
        id: `dm-${Date.now()}`,
        content: 'I understand. What would you like to do next?',
        timestamp: new Date(),
        isVisible: true,
      };
      
      setMessages(prev => {
        const updatedMessages = [...prev, dmResponse];
        // If we have more than 2 messages, mark older ones as not visible
        if (updatedMessages.length > 2) {
          const visibleCount = updatedMessages.filter(m => m.isVisible).length;
          if (visibleCount > 2) {
            // Find the oldest visible message and mark it as not visible
            const oldestVisibleIndex = updatedMessages.findIndex(m => m.isVisible);
            if (oldestVisibleIndex !== -1) {
              updatedMessages[oldestVisibleIndex] = {
                ...updatedMessages[oldestVisibleIndex],
                isVisible: false,
              };
            }
          }
        }
        return updatedMessages;
      });
    }, 1000);
  };
  
  return (
    <div className="dungeon-master-widget">
      <div className="dm-messages">
        {messages.map(message => (
          <div 
            key={message.id} 
            className={`dm-message ${message.isVisible ? 'visible' : 'hidden'}`}
          >
            <p>{message.content}</p>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <form className="dm-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          placeholder="Type your response..."
          className="dm-input-field"
        />
        <button type="submit" className="dm-send-button">
          Send
        </button>
      </form>
    </div>
  );
};

export default DungeonMasterWidget;
