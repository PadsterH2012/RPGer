import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useSocket } from '../../context/SocketContext';
import { useTheme } from '../../context/ThemeContext';
import { WidgetProps, WidgetCategory } from '../../types/widget';
import withWidget from './withWidget';

const NotesContainer = styled.div`
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const NotesTextarea = styled.textarea`
  flex: 1;
  resize: none;
  padding: var(--spacing-md);
  font-family: var(--font-primary);
  font-size: var(--font-size-md);
  border: 1px solid var(--${props => props.theme}-border);
  border-radius: var(--border-radius-sm);
  background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)'};
  color: var(--${props => props.theme}-text-primary);

  &:focus {
    outline: none;
    border-color: var(--${props => props.theme}-primary);
  }
`;

const NotesControls = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: var(--spacing-sm);
`;

const SaveButton = styled.button`
  background-color: var(--${props => props.theme}-primary);
  color: ${props => props.theme === 'dark' ? 'black' : 'white'};
  border: none;
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
  transition: background-color var(--transition-fast) ease;

  &:hover {
    background-color: var(--${props => props.theme}-primary-variant);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const SaveStatus = styled.div<{ saved: boolean }>`
  font-size: var(--font-size-sm);
  color: ${props => props.saved ? 'var(--dark-secondary)' : 'var(--dark-text-secondary)'};
`;

interface NotesWidgetConfig {
  placeholder: string;
  autoSave: boolean;
  autoSaveInterval: number;
  storageKey: string;
  readOnly: boolean;
}

const defaultConfig: NotesWidgetConfig = {
  placeholder: "Type your notes here...",
  autoSave: false,
  autoSaveInterval: 30000, // 30 seconds
  storageKey: 'playerNotes',
  readOnly: false
};

const NotesWidget: React.FC<WidgetProps> = ({ id, config }) => {
  const { theme } = useTheme();
  const { socket, isConnected } = useSocket();
  const widgetConfig = { ...defaultConfig, ...config } as NotesWidgetConfig;

  const [notes, setNotes] = useState('');
  const [savedNotes, setSavedNotes] = useState('');
  const [isSaved, setIsSaved] = useState(true);
  const [lastSaved, setLastSaved] = useState<string | null>(null);

  // Load notes from localStorage on mount
  useEffect(() => {
    const storedNotes = localStorage.getItem(widgetConfig.storageKey);
    if (storedNotes) {
      setNotes(storedNotes);
      setSavedNotes(storedNotes);
    }
  }, [widgetConfig.storageKey]);

  // Auto-save notes if enabled
  useEffect(() => {
    if (widgetConfig.autoSave && !isSaved) {
      const timer = setTimeout(() => {
        saveNotes();
      }, widgetConfig.autoSaveInterval);

      return () => {
        clearTimeout(timer);
      };
    }
  }, [notes, isSaved, widgetConfig.autoSave, widgetConfig.autoSaveInterval]);

  // Listen for notes updates from server
  useEffect(() => {
    if (socket && isConnected) {
      socket.on('notes:update', (updatedNotes: string) => {
        setNotes(updatedNotes);
        setSavedNotes(updatedNotes);
        setIsSaved(true);
        setLastSaved(new Date().toLocaleTimeString());
      });

      // Request initial notes
      socket.emit('notes:request');

      return () => {
        socket.off('notes:update');
      };
    }
  }, [socket, isConnected]);

  // Check if notes have changed
  useEffect(() => {
    setIsSaved(notes === savedNotes);
  }, [notes, savedNotes]);

  const handleNotesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setNotes(e.target.value);
  };

  const saveNotes = () => {
    // Save to localStorage
    localStorage.setItem(widgetConfig.storageKey, notes);
    setSavedNotes(notes);
    setIsSaved(true);
    setLastSaved(new Date().toLocaleTimeString());

    // Send to server if connected
    if (socket && isConnected) {
      socket.emit('notes:save', notes);
    }
  };

  return (
    <NotesContainer>
      <NotesTextarea
        value={notes}
        onChange={handleNotesChange}
        placeholder={widgetConfig.placeholder}
        theme={theme}
        readOnly={widgetConfig.readOnly}
      />
      {!widgetConfig.readOnly && (
        <NotesControls>
          <SaveStatus saved={isSaved}>
            {isSaved
              ? lastSaved ? `Last saved at ${lastSaved}` : 'All changes saved'
              : 'Unsaved changes'}
          </SaveStatus>
          <SaveButton
            onClick={saveNotes}
            disabled={isSaved}
            theme={theme}
          >
            Save Notes
          </SaveButton>
        </NotesControls>
      )}
    </NotesContainer>
  );
};

export default withWidget(NotesWidget, {
  metadata: {
    name: 'Notes',
    description: 'Take and save notes',
    category: WidgetCategory.UTILITY,
    icon: '📝',
    defaultSize: {
      w: 6,
      h: 3,
    },
    minW: 3,
    minH: 2,
  },
  defaultConfig,
});
