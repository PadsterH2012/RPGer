import React, { useState } from 'react';
import styled from 'styled-components';
import { useTheme } from '../context/ThemeContext';

const SettingsContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;

const SettingsHeader = styled.div`
  margin-bottom: var(--spacing-lg);
`;

const SettingsSection = styled.section`
  background-color: var(--${props => props.theme}-surface);
  border: 1px solid var(--${props => props.theme}-border);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
`;

const SectionTitle = styled.h3`
  margin-top: 0;
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-lg);
  color: var(--${props => props.theme}-primary);
`;

const SettingRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--${props => props.theme}-border);

  &:last-child {
    border-bottom: none;
  }
`;

const SettingLabel = styled.div`
  font-weight: 500;
`;

const SettingDescription = styled.div`
  font-size: var(--font-size-sm);
  color: var(--${props => props.theme}-text-secondary);
  margin-top: var(--spacing-xs);
`;

const SettingControl = styled.div`
  display: flex;
  align-items: center;
`;

const Select = styled.select`
  background-color: var(--${props => props.theme}-surface);
  color: var(--${props => props.theme}-text-primary);
  border: 1px solid var(--${props => props.theme}-border);
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-md);
`;

const Button = styled.button`
  background-color: var(--${props => props.theme}-primary);
  color: ${props => props.theme === 'dark' ? 'black' : 'white'};
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-md);
  transition: background-color var(--transition-fast) ease;

  &:hover {
    background-color: var(--${props => props.theme}-primary-variant);
  }
`;

const Switch = styled.label`
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
`;

const SwitchInput = styled.input`
  opacity: 0;
  width: 0;
  height: 0;

  &:checked + span {
    background-color: var(--${props => props.theme}-primary);
  }

  &:checked + span:before {
    transform: translateX(26px);
  }
`;

const SwitchSlider = styled.span`
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--${props => props.theme}-text-secondary);
  transition: var(--transition-fast);
  border-radius: 34px;

  &:before {
    position: absolute;
    content: "";
    height: 26px;
    width: 26px;
    left: 4px;
    bottom: 4px;
    background-color: white;
    transition: var(--transition-fast);
    border-radius: 50%;
  }
`;

const Settings: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const [fontSize, setFontSize] = useState('medium');
  const [fontFamily, setFontFamily] = useState('Roboto');
  const [autoSave, setAutoSave] = useState(true);
  const [snapToGrid, setSnapToGrid] = useState(true);
  const [snapToComponent, setSnapToComponent] = useState(true);

  const handleThemeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setTheme(e.target.value as 'light' | 'dark');
  };

  const handleFontSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFontSize(e.target.value);
    // Apply font size change
    document.documentElement.style.fontSize = {
      small: '14px',
      medium: '16px',
      large: '18px',
      'extra-large': '20px',
    }[e.target.value] || '16px';
  };

  const handleFontFamilyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFontFamily(e.target.value);
    // Apply font family change
    document.documentElement.style.setProperty('--font-primary', e.target.value);
  };

  const handleAutoSaveChange = () => {
    setAutoSave(!autoSave);
    // Save setting to localStorage
    localStorage.setItem('autoSave', (!autoSave).toString());
  };

  const handleSnapToGridChange = () => {
    setSnapToGrid(!snapToGrid);
    // Save setting to localStorage
    localStorage.setItem('snapToGrid', (!snapToGrid).toString());
  };

  const handleSnapToComponentChange = () => {
    setSnapToComponent(!snapToComponent);
    // Save setting to localStorage
    localStorage.setItem('snapToComponent', (!snapToComponent).toString());
  };

  const resetSettings = () => {
    // Reset all settings to defaults
    setTheme('dark');
    setFontSize('medium');
    setFontFamily('Roboto');
    setAutoSave(true);
    setSnapToGrid(true);
    setSnapToComponent(true);
    
    // Apply changes
    document.documentElement.style.fontSize = '16px';
    document.documentElement.style.setProperty('--font-primary', 'Roboto');
    
    // Save to localStorage
    localStorage.setItem('theme', 'dark');
    localStorage.setItem('fontSize', 'medium');
    localStorage.setItem('fontFamily', 'Roboto');
    localStorage.setItem('autoSave', 'true');
    localStorage.setItem('snapToGrid', 'true');
    localStorage.setItem('snapToComponent', 'true');
    
    alert('Settings have been reset to defaults.');
  };

  return (
    <SettingsContainer>
      <SettingsHeader>
        <h2>Settings</h2>
        <p>Customize your dashboard experience</p>
      </SettingsHeader>
      
      <SettingsSection theme={theme}>
        <SectionTitle theme={theme}>Appearance</SectionTitle>
        
        <SettingRow>
          <div>
            <SettingLabel>Theme</SettingLabel>
            <SettingDescription>Choose between light and dark theme</SettingDescription>
          </div>
          <SettingControl>
            <Select value={theme} onChange={handleThemeChange} theme={theme}>
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </Select>
          </SettingControl>
        </SettingRow>
        
        <SettingRow>
          <div>
            <SettingLabel>Font Size</SettingLabel>
            <SettingDescription>Adjust the size of text throughout the application</SettingDescription>
          </div>
          <SettingControl>
            <Select value={fontSize} onChange={handleFontSizeChange} theme={theme}>
              <option value="small">Small</option>
              <option value="medium">Medium</option>
              <option value="large">Large</option>
              <option value="extra-large">Extra Large</option>
            </Select>
          </SettingControl>
        </SettingRow>
        
        <SettingRow>
          <div>
            <SettingLabel>Font Family</SettingLabel>
            <SettingDescription>Choose your preferred font</SettingDescription>
          </div>
          <SettingControl>
            <Select value={fontFamily} onChange={handleFontFamilyChange} theme={theme}>
              <option value="Roboto">Roboto</option>
              <option value="Poppins">Poppins</option>
              <option value="Arial">Arial</option>
              <option value="Verdana">Verdana</option>
            </Select>
          </SettingControl>
        </SettingRow>
      </SettingsSection>
      
      <SettingsSection theme={theme}>
        <SectionTitle theme={theme}>Dashboard</SectionTitle>
        
        <SettingRow>
          <div>
            <SettingLabel>Auto-save Layout</SettingLabel>
            <SettingDescription>Automatically save layout changes</SettingDescription>
          </div>
          <SettingControl>
            <Switch>
              <SwitchInput 
                type="checkbox" 
                checked={autoSave} 
                onChange={handleAutoSaveChange}
                theme={theme}
              />
              <SwitchSlider theme={theme} />
            </Switch>
          </SettingControl>
        </SettingRow>
        
        <SettingRow>
          <div>
            <SettingLabel>Snap to Grid</SettingLabel>
            <SettingDescription>Snap widgets to grid when moving</SettingDescription>
          </div>
          <SettingControl>
            <Switch>
              <SwitchInput 
                type="checkbox" 
                checked={snapToGrid} 
                onChange={handleSnapToGridChange}
                theme={theme}
              />
              <SwitchSlider theme={theme} />
            </Switch>
          </SettingControl>
        </SettingRow>
        
        <SettingRow>
          <div>
            <SettingLabel>Snap to Component</SettingLabel>
            <SettingDescription>Snap widgets to other components when moving</SettingDescription>
          </div>
          <SettingControl>
            <Switch>
              <SwitchInput 
                type="checkbox" 
                checked={snapToComponent} 
                onChange={handleSnapToComponentChange}
                theme={theme}
              />
              <SwitchSlider theme={theme} />
            </Switch>
          </SettingControl>
        </SettingRow>
      </SettingsSection>
      
      <div style={{ textAlign: 'center', marginTop: 'var(--spacing-xl)' }}>
        <Button onClick={resetSettings} theme={theme}>Reset All Settings</Button>
      </div>
    </SettingsContainer>
  );
};

export default Settings;
