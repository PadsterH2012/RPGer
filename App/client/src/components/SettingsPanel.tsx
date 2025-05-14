import React, { useState, useEffect } from 'react';
import '../styles/SettingsPanel.css';

// Define settings types
interface ThemeSettings {
  primaryColor: string;
  secondaryColor: string;
  backgroundColor: string;
  textColor: string;
  fontFamily: string;
  fontSize: string;
}

interface AnimationSettings {
  speed: 'slow' | 'medium' | 'fast';
  enabled: boolean;
}

interface LayoutSettings {
  showPlayerStats: boolean;
  showEnvironment: boolean;
  showActionResults: boolean;
  showDungeonMaster: boolean;
  showAgentDebug: boolean;
  layoutName: string;
}

interface Settings {
  theme: ThemeSettings;
  animation: AnimationSettings;
  layout: LayoutSettings;
}

// Default settings
const defaultSettings: Settings = {
  theme: {
    primaryColor: '#6200ee',
    secondaryColor: '#03dac6',
    backgroundColor: '#f5f5f5',
    textColor: '#333333',
    fontFamily: 'Arial, sans-serif',
    fontSize: 'medium',
  },
  animation: {
    speed: 'medium',
    enabled: true,
  },
  layout: {
    showPlayerStats: true,
    showEnvironment: true,
    showActionResults: true,
    showDungeonMaster: true,
    showAgentDebug: true,
    layoutName: 'Default',
  },
};

// Predefined themes
const predefinedThemes = {
  purple: {
    primaryColor: '#6200ee',
    secondaryColor: '#03dac6',
    backgroundColor: '#f5f5f5',
    textColor: '#333333',
    fontFamily: 'Arial, sans-serif',
    fontSize: 'medium',
  },
  dark: {
    primaryColor: '#bb86fc',
    secondaryColor: '#03dac6',
    backgroundColor: '#121212',
    textColor: '#e0e0e0',
    fontFamily: 'Arial, sans-serif',
    fontSize: 'medium',
  },
  fantasy: {
    primaryColor: '#8b4513',
    secondaryColor: '#228b22',
    backgroundColor: '#f5f5dc',
    textColor: '#333333',
    fontFamily: 'MedievalSharp, cursive',
    fontSize: 'medium',
  },
  modern: {
    primaryColor: '#1976d2',
    secondaryColor: '#ff5722',
    backgroundColor: '#ffffff',
    textColor: '#212121',
    fontFamily: 'Roboto, sans-serif',
    fontSize: 'medium',
  },
};

// Font options
const fontOptions = [
  { value: 'Arial, sans-serif', label: 'Arial' },
  { value: 'Times New Roman, serif', label: 'Times New Roman' },
  { value: 'Courier New, monospace', label: 'Courier New' },
  { value: 'Georgia, serif', label: 'Georgia' },
  { value: 'Verdana, sans-serif', label: 'Verdana' },
  { value: 'Roboto, sans-serif', label: 'Roboto' },
  { value: 'MedievalSharp, cursive', label: 'Medieval' },
];

// Font size options
const fontSizeOptions = [
  { value: 'small', label: 'Small' },
  { value: 'medium', label: 'Medium' },
  { value: 'large', label: 'Large' },
  { value: 'x-large', label: 'Extra Large' },
];

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onApplySettings: (settings: Settings) => void;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({ isOpen, onClose, onApplySettings }) => {
  const [settings, setSettings] = useState<Settings>(defaultSettings);
  const [activeTab, setActiveTab] = useState<'theme' | 'animation' | 'layout'>('theme');
  const [savedLayouts, setSavedLayouts] = useState<string[]>(['Default']);
  const [newLayoutName, setNewLayoutName] = useState('');

  // Load settings from localStorage on component mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('rpgerSettings');
    if (savedSettings) {
      try {
        setSettings(JSON.parse(savedSettings));
      } catch (error) {
        console.error('Error loading saved settings:', error);
      }
    }

    const savedLayoutNames = localStorage.getItem('rpgerSavedLayouts');
    if (savedLayoutNames) {
      try {
        setSavedLayouts(JSON.parse(savedLayoutNames));
      } catch (error) {
        console.error('Error loading saved layout names:', error);
      }
    }
  }, []);

  // Handle theme change
  const handleThemeChange = (theme: keyof typeof predefinedThemes) => {
    setSettings(prev => ({
      ...prev,
      theme: predefinedThemes[theme],
    }));
  };

  // Handle theme setting change
  const handleThemeSettingChange = (setting: keyof ThemeSettings, value: string) => {
    setSettings(prev => ({
      ...prev,
      theme: {
        ...prev.theme,
        [setting]: value,
      },
    }));
  };

  // Handle animation setting change
  const handleAnimationSettingChange = (setting: keyof AnimationSettings, value: any) => {
    setSettings(prev => ({
      ...prev,
      animation: {
        ...prev.animation,
        [setting]: value,
      },
    }));
  };

  // Handle layout setting change
  const handleLayoutSettingChange = (setting: keyof LayoutSettings, value: any) => {
    setSettings(prev => ({
      ...prev,
      layout: {
        ...prev.layout,
        [setting]: value,
      },
    }));
  };

  // Save current layout
  const saveCurrentLayout = () => {
    if (!newLayoutName.trim()) return;

    const layoutToSave = {
      ...settings.layout,
      layoutName: newLayoutName,
    };

    setSettings(prev => ({
      ...prev,
      layout: layoutToSave,
    }));

    if (!savedLayouts.includes(newLayoutName)) {
      const updatedLayouts = [...savedLayouts, newLayoutName];
      setSavedLayouts(updatedLayouts);
      localStorage.setItem('rpgerSavedLayouts', JSON.stringify(updatedLayouts));
    }

    localStorage.setItem(`rpgerLayout_${newLayoutName}`, JSON.stringify(layoutToSave));
    setNewLayoutName('');
  };

  // Load saved layout
  const loadSavedLayout = (layoutName: string) => {
    const savedLayout = localStorage.getItem(`rpgerLayout_${layoutName}`);
    if (savedLayout) {
      try {
        const parsedLayout = JSON.parse(savedLayout);
        setSettings(prev => ({
          ...prev,
          layout: parsedLayout,
        }));
      } catch (error) {
        console.error('Error loading saved layout:', error);
      }
    }
  };

  // Apply settings
  const applySettings = () => {
    localStorage.setItem('rpgerSettings', JSON.stringify(settings));
    onApplySettings(settings);
    onClose();
  };

  // Reset settings to default
  const resetSettings = () => {
    setSettings(defaultSettings);
  };

  if (!isOpen) return null;

  return (
    <div className="settings-panel-overlay">
      <div className="settings-panel">
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="settings-tabs">
          <button
            className={`tab ${activeTab === 'theme' ? 'active' : ''}`}
            onClick={() => setActiveTab('theme')}
          >
            Theme
          </button>
          <button
            className={`tab ${activeTab === 'animation' ? 'active' : ''}`}
            onClick={() => setActiveTab('animation')}
          >
            Animation
          </button>
          <button
            className={`tab ${activeTab === 'layout' ? 'active' : ''}`}
            onClick={() => setActiveTab('layout')}
          >
            Layout
          </button>
        </div>

        <div className="settings-content">
          {activeTab === 'theme' && (
            <div className="theme-settings">
              <h3>Predefined Themes</h3>
              <div className="theme-presets">
                <button
                  className="theme-preset purple"
                  onClick={() => handleThemeChange('purple')}
                >
                  Purple
                </button>
                <button
                  className="theme-preset dark"
                  onClick={() => handleThemeChange('dark')}
                >
                  Dark
                </button>
                <button
                  className="theme-preset fantasy"
                  onClick={() => handleThemeChange('fantasy')}
                >
                  Fantasy
                </button>
                <button
                  className="theme-preset modern"
                  onClick={() => handleThemeChange('modern')}
                >
                  Modern
                </button>
              </div>

              <h3>Custom Theme</h3>
              <div className="setting-group">
                <label>
                  Primary Color:
                  <input
                    type="color"
                    value={settings.theme.primaryColor}
                    onChange={(e) => handleThemeSettingChange('primaryColor', e.target.value)}
                  />
                </label>
              </div>

              <div className="setting-group">
                <label>
                  Secondary Color:
                  <input
                    type="color"
                    value={settings.theme.secondaryColor}
                    onChange={(e) => handleThemeSettingChange('secondaryColor', e.target.value)}
                  />
                </label>
              </div>

              <div className="setting-group">
                <label>
                  Background Color:
                  <input
                    type="color"
                    value={settings.theme.backgroundColor}
                    onChange={(e) => handleThemeSettingChange('backgroundColor', e.target.value)}
                  />
                </label>
              </div>

              <div className="setting-group">
                <label>
                  Text Color:
                  <input
                    type="color"
                    value={settings.theme.textColor}
                    onChange={(e) => handleThemeSettingChange('textColor', e.target.value)}
                  />
                </label>
              </div>

              <div className="setting-group">
                <label>
                  Font Family:
                  <select
                    value={settings.theme.fontFamily}
                    onChange={(e) => handleThemeSettingChange('fontFamily', e.target.value)}
                  >
                    {fontOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="setting-group">
                <label>
                  Font Size:
                  <select
                    value={settings.theme.fontSize}
                    onChange={(e) => handleThemeSettingChange('fontSize', e.target.value)}
                  >
                    {fontSizeOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            </div>
          )}

          {activeTab === 'animation' && (
            <div className="animation-settings">
              <div className="setting-group">
                <label>
                  Animation Speed:
                  <select
                    value={settings.animation.speed}
                    onChange={(e) => handleAnimationSettingChange('speed', e.target.value)}
                  >
                    <option value="slow">Slow</option>
                    <option value="medium">Medium</option>
                    <option value="fast">Fast</option>
                  </select>
                </label>
              </div>

              <div className="setting-group">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.animation.enabled}
                    onChange={(e) => handleAnimationSettingChange('enabled', e.target.checked)}
                  />
                  Enable Animations
                </label>
              </div>
            </div>
          )}

          {activeTab === 'layout' && (
            <div className="layout-settings">
              <h3>Widget Visibility</h3>
              <div className="setting-group">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.layout.showPlayerStats}
                    onChange={(e) => handleLayoutSettingChange('showPlayerStats', e.target.checked)}
                  />
                  Show Player Stats
                </label>
              </div>

              <div className="setting-group">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.layout.showEnvironment}
                    onChange={(e) => handleLayoutSettingChange('showEnvironment', e.target.checked)}
                  />
                  Show Environment
                </label>
              </div>

              <div className="setting-group">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.layout.showActionResults}
                    onChange={(e) => handleLayoutSettingChange('showActionResults', e.target.checked)}
                  />
                  Show Action Results
                </label>
              </div>

              <div className="setting-group">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.layout.showDungeonMaster}
                    onChange={(e) => handleLayoutSettingChange('showDungeonMaster', e.target.checked)}
                  />
                  Show Dungeon Master
                </label>
              </div>

              <div className="setting-group">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.layout.showAgentDebug}
                    onChange={(e) => handleLayoutSettingChange('showAgentDebug', e.target.checked)}
                  />
                  Show Agent Debug
                </label>
              </div>

              <h3>Saved Layouts</h3>
              <div className="saved-layouts">
                {savedLayouts.map(layout => (
                  <button
                    key={layout}
                    className="layout-button"
                    onClick={() => loadSavedLayout(layout)}
                  >
                    {layout}
                  </button>
                ))}
              </div>

              <div className="save-layout">
                <input
                  type="text"
                  value={newLayoutName}
                  onChange={(e) => setNewLayoutName(e.target.value)}
                  placeholder="New layout name"
                />
                <button onClick={saveCurrentLayout}>Save Layout</button>
              </div>
            </div>
          )}
        </div>

        <div className="settings-footer">
          <button className="reset-button" onClick={resetSettings}>
            Reset to Default
          </button>
          <button className="apply-button" onClick={applySettings}>
            Apply Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;
