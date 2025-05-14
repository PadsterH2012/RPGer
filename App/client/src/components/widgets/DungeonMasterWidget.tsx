import React, { useState, useEffect, useRef } from 'react';
import { useSocket } from '../../context/SocketContext';
import '../../styles/widgets/DungeonMasterWidget.css';

// Define DM message type
interface DMMessage {
  id: string;
  content: string;
  timestamp: Date;
  isVisible: boolean;
}

// Define game state interface
interface GameState {
  dm_messages: string[];
  [key: string]: any;
}

const DungeonMasterWidget: React.FC = () => {
  const { socket, isConnected } = useSocket();
  const [messages, setMessages] = useState<DMMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [maxVisibleMessages, setMaxVisibleMessages] = useState(3);
  const [gameStarted, setGameStarted] = useState(false);

  // Listen for game state updates from the server
  useEffect(() => {
    if (socket && isConnected) {
      // Request initial game state
      socket.emit('get_game_state');

      // Listen for game state updates
      const handleGameStateUpdate = (gameState: GameState) => {
        if (gameState.dm_messages && gameState.dm_messages.length > 0) {
          // Convert server messages to DMMessage format
          const newMessages = gameState.dm_messages.map((content, index) => ({
            id: `server-${Date.now()}-${index}`,
            content,
            timestamp: new Date(),
            isVisible: true,
          }));

          // Update messages state, keeping track of previously processed messages
          setMessages(prev => {
            // Get existing message contents for comparison
            const existingContents = new Set(prev.map(m => m.content));

            // Filter out messages that already exist
            const uniqueNewMessages = newMessages.filter(m => !existingContents.has(m.content));

            if (uniqueNewMessages.length === 0) {
              return prev; // No new messages to add
            }

            // Combine existing and new messages
            const updatedMessages = [...prev, ...uniqueNewMessages];

            // If we have more than maxVisibleMessages, mark older ones as not visible
            if (updatedMessages.length > maxVisibleMessages) {
              const visibleCount = updatedMessages.filter(m => m.isVisible).length;
              if (visibleCount > maxVisibleMessages) {
                // Find the oldest visible messages and mark them as not visible
                let hiddenCount = 0;
                const messagesToHide = visibleCount - maxVisibleMessages;

                return updatedMessages.map((msg, idx) => {
                  if (msg.isVisible && hiddenCount < messagesToHide) {
                    hiddenCount++;
                    return { ...msg, isVisible: false };
                  }
                  return msg;
                });
              }
            }

            return updatedMessages;
          });
        }
      };

      socket.on('game_state_update', handleGameStateUpdate);

      // Cleanup listener on unmount
      return () => {
        socket.off('game_state_update', handleGameStateUpdate);
      };
    }
  }, [socket, isConnected, maxVisibleMessages]);

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

    // Add player message to the UI immediately
    const playerMessage: DMMessage = {
      id: `player-${Date.now()}`,
      content: `Player: ${inputValue}`,
      timestamp: new Date(),
      isVisible: true,
    };

    setMessages(prev => {
      const updatedMessages = [...prev, playerMessage];
      // If we have more than maxVisibleMessages, mark older ones as not visible
      if (updatedMessages.length > maxVisibleMessages) {
        const visibleCount = updatedMessages.filter(m => m.isVisible).length;
        if (visibleCount > maxVisibleMessages) {
          // Find the oldest visible messages and mark them as not visible
          let hiddenCount = 0;
          const messagesToHide = visibleCount - maxVisibleMessages;

          return updatedMessages.map((msg, idx) => {
            if (msg.isVisible && hiddenCount < messagesToHide) {
              hiddenCount++;
              return { ...msg, isVisible: false };
            }
            return msg;
          });
        }
      }
      return updatedMessages;
    });

    // Send command to server if connected
    if (socket && isConnected) {
      socket.emit('command', { command: inputValue });
      console.log('Sent command to server:', inputValue);
    } else {
      console.warn('Socket not connected, command not sent');

      // If not connected, add a fallback message
      setTimeout(() => {
        const fallbackMessage: DMMessage = {
          id: `fallback-${Date.now()}`,
          content: 'Not connected to server. Please check your connection.',
          timestamp: new Date(),
          isVisible: true,
        };

        setMessages(prev => [...prev, fallbackMessage]);
      }, 500);
    }

    // Clear input
    setInputValue('');
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
