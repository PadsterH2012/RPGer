/**
 * TextWidget Component
 * 
 * Widget for displaying formatted text content.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useTheme } from '../../context/ThemeContext';
import { WidgetProps, WidgetCategory } from '../../types/widget';
import withWidget from './withWidget';

const TextContainer = styled.div`
  height: 100%;
  overflow-y: auto;
  font-family: var(--font-family);
`;

const TextContent = styled.div<{ fontSize: string; textAlign: string; fontWeight: string }>`
  font-size: ${props => props.fontSize};
  text-align: ${props => props.textAlign};
  font-weight: ${props => props.fontWeight};
  line-height: 1.5;
  white-space: pre-wrap;
`;

const EditableTextarea = styled.textarea`
  width: 100%;
  height: 100%;
  min-height: 100px;
  resize: none;
  border: 1px solid var(--${props => props.theme}-border);
  background-color: var(--${props => props.theme}-surface);
  color: var(--${props => props.theme}-text-primary);
  font-family: var(--font-family);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  
  &:focus {
    outline: none;
    border-color: var(--${props => props.theme}-primary);
  }
`;

const ControlsContainer = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--spacing-sm);
`;

const Button = styled.button`
  background-color: var(--${props => props.theme}-primary);
  color: ${props => props.theme === 'dark' ? 'black' : 'white'};
  border: none;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
  
  &:hover {
    background-color: var(--${props => props.theme}-primary-variant);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const SaveStatus = styled.div<{ saved: boolean }>`
  font-size: var(--font-size-xs);
  color: ${props => props.saved ? 'var(--success)' : 'var(--warning)'};
`;

interface TextWidgetConfig {
  content: string;
  fontSize: string;
  textAlign: string;
  fontWeight: string;
  lastSaved?: string;
}

const defaultConfig: TextWidgetConfig = {
  content: 'Enter your text here...',
  fontSize: 'var(--font-size-md)',
  textAlign: 'left',
  fontWeight: 'normal',
};

const TextWidget: React.FC<WidgetProps> = ({ id, config, onConfigChange, isEditing }) => {
  const { theme } = useTheme();
  const widgetConfig = { ...defaultConfig, ...config } as TextWidgetConfig;
  
  const [text, setText] = useState(widgetConfig.content);
  const [isEditable, setIsEditable] = useState(!!isEditing);
  const [isSaved, setIsSaved] = useState(true);
  
  // Update text when config changes
  useEffect(() => {
    if (widgetConfig.content !== text) {
      setText(widgetConfig.content);
    }
  }, [widgetConfig.content]);
  
  // Check if text has changed
  useEffect(() => {
    setIsSaved(text === widgetConfig.content);
  }, [text, widgetConfig.content]);
  
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
  };
  
  const handleSave = () => {
    if (onConfigChange) {
      onConfigChange({
        ...widgetConfig,
        content: text,
        lastSaved: new Date().toLocaleTimeString(),
      });
    }
    setIsSaved(true);
  };
  
  const toggleEdit = () => {
    setIsEditable(!isEditable);
    
    // Save when exiting edit mode
    if (isEditable && !isSaved) {
      handleSave();
    }
  };
  
  return (
    <TextContainer>
      {isEditable ? (
        <>
          <ControlsContainer>
            <Button onClick={toggleEdit} theme={theme}>
              Done Editing
            </Button>
            <SaveStatus saved={isSaved}>
              {isSaved 
                ? widgetConfig.lastSaved ? `Last saved at ${widgetConfig.lastSaved}` : 'All changes saved' 
                : 'Unsaved changes'}
            </SaveStatus>
            <Button onClick={handleSave} disabled={isSaved} theme={theme}>
              Save
            </Button>
          </ControlsContainer>
          <EditableTextarea
            value={text}
            onChange={handleTextChange}
            theme={theme}
          />
        </>
      ) : (
        <>
          <ControlsContainer>
            <Button onClick={toggleEdit} theme={theme}>
              Edit Text
            </Button>
          </ControlsContainer>
          <TextContent
            fontSize={widgetConfig.fontSize}
            textAlign={widgetConfig.textAlign}
            fontWeight={widgetConfig.fontWeight}
          >
            {text}
          </TextContent>
        </>
      )}
    </TextContainer>
  );
};

export default withWidget(TextWidget, {
  metadata: {
    name: 'Text',
    description: 'Display formatted text content',
    category: WidgetCategory.UTILITY,
    icon: '📝',
    defaultSize: {
      w: 6,
      h: 2,
    },
    minW: 2,
    minH: 1,
  },
  defaultConfig,
});
