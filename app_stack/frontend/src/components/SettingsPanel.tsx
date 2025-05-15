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

interface WidgetSettings {
  playerStats: boolean;
  environment: boolean;
  actionResults: boolean;
  dungeonMaster: boolean;
  agentDebug: boolean;
  connectionStatus: boolean;
}

interface LayoutSettings {
  name: string;
  isDefault: boolean;
}

interface Settings {
  theme: ThemeSettings;
  animation: AnimationSettings;
  widgets: WidgetSettings;
  layout: LayoutSettings;
}

// Preset themes
const presetThemes = {
  modern: {
    name: 'Modern Purple',
    primaryColor: '#8b5cf6',
    secondaryColor: '#10b981',
    backgroundColor: '#f9fafb',
    textColor: '#333333',
    fontFamily: 'Inter, sans-serif',
    fontSize: 'medium',
  },
  dark: {
    name: 'Dark Mode',
    primaryColor: '#7c3aed',
    secondaryColor: '#06b6d4',
    backgroundColor: '#111827',
    textColor: '#f3f4f6',
    fontFamily: 'Inter, sans-serif',
    fontSize: 'medium',
  },
  fantasy: {
    name: 'Fantasy',
    primaryColor: '#b45309',
    secondaryColor: '#065f46',
    backgroundColor: '#fef3c7',
    textColor: '#422006',
    fontFamily: 'MedievalSharp, cursive',
    fontSize: 'medium',
  },
  cyberpunk: {
    name: 'Cyberpunk',
    primaryColor: '#f59e0b',
    secondaryColor: '#ec4899',
    backgroundColor: '#0f172a',
    textColor: '#f8fafc',
    fontFamily: 'Courier New, monospace',
    fontSize: 'medium',
  },
  pastel: {
    name: 'Pastel',
    primaryColor: '#c084fc',
    secondaryColor: '#67e8f9',
    backgroundColor: '#f8fafc',
    textColor: '#334155',
    fontFamily: 'Roboto, sans-serif',
    fontSize: 'medium',
  },
  retro: {
    name: 'Retro',
    primaryColor: '#ef4444',
    secondaryColor: '#facc15',
    backgroundColor: '#fecaca',
    textColor: '#7f1d1d',
    fontFamily: 'Courier New, monospace',
    fontSize: 'medium',
  },
  dungeon: {
    name: 'Dungeon Master',
    primaryColor: '#4b5563',
    secondaryColor: '#b91c1c',
    backgroundColor: '#1f2937',
    textColor: '#e5e7eb',
    fontFamily: 'MedievalSharp, cursive',
    fontSize: 'medium',
  },
  forest: {
    name: 'Enchanted Forest',
    primaryColor: '#047857',
    secondaryColor: '#7c2d12',
    backgroundColor: '#064e3b',
    textColor: '#d1fae5',
    fontFamily: 'Georgia, serif',
    fontSize: 'medium',
  },
  parchment: {
    name: 'Ancient Parchment',
    primaryColor: '#92400e',
    secondaryColor: '#3f6212',
    backgroundColor: '#fef3c7',
    textColor: '#422006',
    fontFamily: 'Georgia, serif',
    fontSize: 'medium',
  },
};

// Default settings
const defaultSettings: Settings = {
  theme: {
    primaryColor: presetThemes.modern.primaryColor,
    secondaryColor: presetThemes.modern.secondaryColor,
    backgroundColor: presetThemes.modern.backgroundColor,
    textColor: presetThemes.modern.textColor,
    fontFamily: presetThemes.modern.fontFamily,
    fontSize: presetThemes.modern.fontSize,
  },
  animation: {
    speed: 'slow',
    enabled: true,
  },
  widgets: {
    playerStats: true,
    environment: true,
    actionResults: true,
    dungeonMaster: true,
    agentDebug: true,
    connectionStatus: true,
  },
  layout: {
    name: 'Default',
    isDefault: true,
  },
};

// Font options
const fontOptions = [
  { value: 'Inter, sans-serif', label: 'Inter' },
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
  { value: 'small', label: 'Small (14px)' },
  { value: 'medium', label: 'Medium (16px)' },
  { value: 'large', label: 'Large (18px)' },
  { value: 'x-large', label: 'Extra Large (20px)' },
];

// Animation speed options
const animationSpeedOptions = [
  { value: 'slow', label: 'Slow' },
  { value: 'medium', label: 'Medium' },
  { value: 'fast', label: 'Fast' },
];

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onApplySettings: (settings: Settings) => void;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({ isOpen, onClose, onApplySettings }) => {
  const [settings, setSettings] = useState<Settings>(defaultSettings);
  const [activeTab, setActiveTab] = useState<'theme' | 'animation' | 'widgets' | 'layout'>('theme');
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

  // Apply preset theme
  const applyPresetTheme = (presetKey: keyof typeof presetThemes) => {
    const preset = presetThemes[presetKey];
    setSettings(prev => ({
      ...prev,
      theme: {
        primaryColor: preset.primaryColor,
        secondaryColor: preset.secondaryColor,
        backgroundColor: preset.backgroundColor,
        textColor: preset.textColor,
        fontFamily: preset.fontFamily,
        fontSize: preset.fontSize,
      },
    }));
  };

  // Handle animation setting change
  const handleAnimationSettingChange = (setting: keyof AnimationSettings, value: any) => {
    setSettings(prev => {
      // Create default animation object if it doesn't exist
      const currentAnimation = prev.animation || {
        speed: 'medium',
        enabled: true,
      };

      return {
        ...prev,
        animation: {
          ...currentAnimation,
          [setting]: value,
        },
      };
    });
  };

  // Handle widget setting change
  const handleWidgetSettingChange = (setting: keyof WidgetSettings, value: boolean) => {
    setSettings(prev => {
      // Create default widgets object if it doesn't exist
      const currentWidgets = prev.widgets || {
        playerStats: true,
        environment: true,
        actionResults: true,
        dungeonMaster: true,
        agentDebug: true,
      };

      return {
        ...prev,
        widgets: {
          ...currentWidgets,
          [setting]: value,
        },
      };
    });
  };

  // Handle layout setting change - keeping for future use
  /*
  const handleLayoutSettingChange = (setting: keyof LayoutSettings, value: any) => {
    setSettings(prev => ({
      ...prev,
      layout: {
        ...prev.layout,
        [setting]: value,
      },
    }));
  };
  */

  // Save current layout
  const saveCurrentLayout = () => {
    if (!newLayoutName.trim()) return;

    // Create default layout if it doesn't exist
    const currentLayout = settings.layout || {
      name: 'Default',
      isDefault: true,
    };

    const layoutToSave = {
      ...currentLayout,
      name: newLayoutName,
      isDefault: false,
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
    // If loading the Default layout and it doesn't exist in localStorage, create it
    if (layoutName === 'Default' && !localStorage.getItem(`rpgerLayout_Default`)) {
      const defaultLayout = {
        name: 'Default',
        isDefault: true,
      };

      setSettings(prev => ({
        ...prev,
        layout: defaultLayout,
      }));

      return;
    }

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
            className={`tab ${activeTab === 'widgets' ? 'active' : ''}`}
            onClick={() => setActiveTab('widgets')}
          >
            Widgets
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
              <h3 className="theme-settings-heading">Theme Settings</h3>

              <div className="setting-group preset-theme-group">
                <div className="preset-theme-label">Preset Themes:</div>
                <select
                  className="theme-select"
                  value=""
                  onChange={(e) => {
                    if (e.target.value) {
                      applyPresetTheme(e.target.value as keyof typeof presetThemes);
                    }
                  }}
                >
                  <option value="" disabled>Select a theme...</option>
                  {Object.entries(presetThemes).map(([key, theme]) => (
                    <option key={key} value={key}>
                      {theme.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="theme-preview" style={{
                backgroundColor: settings.theme.backgroundColor,
                color: settings.theme.textColor,
                fontFamily: settings.theme.fontFamily,
                padding: '15px',
                borderRadius: '4px',
                marginBottom: '15px',
                border: '1px solid rgba(0,0,0,0.1)'
              }}>
                <div className="preview-title" style={{ marginBottom: '10px', fontWeight: 'bold' }}>Theme Preview</div>
                <div className="preview-content" style={{ marginBottom: '10px', fontSize: settings.theme.fontSize }}>
                  This is how your dashboard will look with this theme.
                </div>
                <div className="preview-buttons">
                  <button style={{
                    backgroundColor: settings.theme.primaryColor,
                    color: '#fff',
                    border: 'none',
                    padding: '5px 10px',
                    borderRadius: '4px',
                    marginRight: '8px',
                    fontFamily: settings.theme.fontFamily
                  }}>
                    Primary
                  </button>
                  <button style={{
                    backgroundColor: settings.theme.secondaryColor,
                    color: '#fff',
                    border: 'none',
                    padding: '5px 10px',
                    borderRadius: '4px',
                    fontFamily: settings.theme.fontFamily
                  }}>
                    Secondary
                  </button>
                </div>
              </div>

              <h4 className="settings-subheading">Custom Colors</h4>

              <div className="setting-group color-setting-group">
                <div className="color-label">Primary Color:</div>
                <div className="color-input-container">
                  <input
                    type="color"
                    value={settings.theme.primaryColor}
                    onChange={(e) => handleThemeSettingChange('primaryColor', e.target.value)}
                    id="primaryColorInput"
                  />
                  <label htmlFor="primaryColorInput" className="color-value">{settings.theme.primaryColor}</label>
                </div>
              </div>

              <div className="setting-group color-setting-group">
                <div className="color-label">Secondary Color:</div>
                <div className="color-input-container">
                  <input
                    type="color"
                    value={settings.theme.secondaryColor}
                    onChange={(e) => handleThemeSettingChange('secondaryColor', e.target.value)}
                    id="secondaryColorInput"
                  />
                  <label htmlFor="secondaryColorInput" className="color-value">{settings.theme.secondaryColor}</label>
                </div>
              </div>

              <div className="setting-group color-setting-group">
                <div className="color-label">Background Color:</div>
                <div className="color-input-container">
                  <input
                    type="color"
                    value={settings.theme.backgroundColor}
                    onChange={(e) => handleThemeSettingChange('backgroundColor', e.target.value)}
                    id="backgroundColorInput"
                  />
                  <label htmlFor="backgroundColorInput" className="color-value">{settings.theme.backgroundColor}</label>
                </div>
              </div>

              <div className="setting-group color-setting-group">
                <div className="color-label">Text Color:</div>
                <div className="color-input-container">
                  <input
                    type="color"
                    value={settings.theme.textColor}
                    onChange={(e) => handleThemeSettingChange('textColor', e.target.value)}
                    id="textColorInput"
                  />
                  <label htmlFor="textColorInput" className="color-value">{settings.theme.textColor}</label>
                </div>
              </div>

              <h4 className="settings-subheading">Typography</h4>

              <div className="setting-group typography-setting-group">
                <div className="typography-label">Font Family:</div>
                <select
                  className="theme-select"
                  value={settings.theme.fontFamily}
                  onChange={(e) => handleThemeSettingChange('fontFamily', e.target.value)}
                >
                  {fontOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="setting-group typography-setting-group">
                <div className="typography-label">Font Size:</div>
                <select
                  className="theme-select"
                  value={settings.theme.fontSize}
                  onChange={(e) => handleThemeSettingChange('fontSize', e.target.value)}
                >
                  {fontSizeOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {activeTab === 'animation' && (
            <div className="animation-settings">
              <h3>Animation Settings</h3>
              <p>Control how animations behave throughout the dashboard.</p>

              <div className="setting-group animation-setting-group">
                <div className="animation-label">Animation Speed:</div>
                <select
                  className="theme-select"
                  value={settings.animation?.speed || 'medium'}
                  onChange={(e) => handleAnimationSettingChange('speed', e.target.value as 'slow' | 'medium' | 'fast')}
                >
                  {animationSpeedOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="setting-group animation-checkbox-group">
                <label className="animation-checkbox-label">
                  <input
                    type="checkbox"
                    checked={settings.animation?.enabled ?? true}
                    onChange={(e) => handleAnimationSettingChange('enabled', e.target.checked)}
                  />
                  <span className="animation-option-text">Enable Animations</span>
                </label>
              </div>

              <div className="animation-preview">
                <h4 className="settings-subheading">Animation Preview</h4>
                <div className="preview-animation-container">
                  <div
                    className="preview-animation-element"
                    style={{
                      animationDuration: settings.animation?.speed === 'slow' ? '2s' :
                                         settings.animation?.speed === 'medium' ? '1s' : '0.5s',
                      animationPlayState: settings.animation?.enabled ? 'running' : 'paused'
                    }}
                  ></div>
                </div>
                <div className="animation-preview-label">
                  {settings.animation?.enabled ?
                    `Animations are enabled (${settings.animation?.speed} speed)` :
                    'Animations are disabled'}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'widgets' && (
            <div className="widgets-settings">
              <h3>Widget Management</h3>
              <p>Select which widgets to display on the dashboard:</p>

              <div className="widget-item">
                <label className="widget-label">
                  <input
                    type="checkbox"
                    checked={settings.widgets?.playerStats ?? true}
                    onChange={(e) => handleWidgetSettingChange('playerStats', e.target.checked)}
                  />
                  <span className="widget-name">Player Stats</span>
                </label>
                <div className="widget-color" style={{ backgroundColor: '#8b5cf6' }}></div>
              </div>

              <div className="widget-item">
                <label className="widget-label">
                  <input
                    type="checkbox"
                    checked={settings.widgets?.environment ?? true}
                    onChange={(e) => handleWidgetSettingChange('environment', e.target.checked)}
                  />
                  <span className="widget-name">Environment</span>
                </label>
                <div className="widget-color" style={{ backgroundColor: '#10b981' }}></div>
              </div>

              <div className="widget-item">
                <label className="widget-label">
                  <input
                    type="checkbox"
                    checked={settings.widgets?.actionResults ?? true}
                    onChange={(e) => handleWidgetSettingChange('actionResults', e.target.checked)}
                  />
                  <span className="widget-name">Action Results</span>
                </label>
                <div className="widget-color" style={{ backgroundColor: '#f59e0b' }}></div>
              </div>

              <div className="widget-item">
                <label className="widget-label">
                  <input
                    type="checkbox"
                    checked={settings.widgets?.dungeonMaster ?? true}
                    onChange={(e) => handleWidgetSettingChange('dungeonMaster', e.target.checked)}
                  />
                  <span className="widget-name">Dungeon Master</span>
                </label>
                <div className="widget-color" style={{ backgroundColor: '#3b82f6' }}></div>
              </div>

              <div className="widget-item">
                <label className="widget-label">
                  <input
                    type="checkbox"
                    checked={settings.widgets?.agentDebug ?? true}
                    onChange={(e) => handleWidgetSettingChange('agentDebug', e.target.checked)}
                  />
                  <span className="widget-name">Agent Debug</span>
                </label>
                <div className="widget-color" style={{ backgroundColor: '#ef4444' }}></div>
              </div>

              <div className="widget-item">
                <label className="widget-label">
                  <input
                    type="checkbox"
                    checked={settings.widgets?.connectionStatus ?? true}
                    onChange={(e) => handleWidgetSettingChange('connectionStatus', e.target.checked)}
                  />
                  <span className="widget-name">Connection Status</span>
                </label>
                <div className="widget-color" style={{ backgroundColor: '#6366f1' }}></div>
              </div>

              <div className="widget-help">
                <h4>Working with Widgets</h4>
                <ul>
                  <li>Drag widgets by their colored headers to reposition them</li>
                  <li>Resize widgets by dragging any corner</li>
                  <li>Widgets can be positioned freely without snapping</li>
                  <li>Changes are saved automatically</li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === 'layout' && (
            <div className="layout-settings">
              <h3>Layout Management</h3>
              <p>Current Layout: {settings.layout?.name || 'Default'}</p>

              <div className="layout-input-group">
                <input
                  type="text"
                  value={newLayoutName}
                  onChange={(e) => setNewLayoutName(e.target.value)}
                  placeholder="Enter layout name"
                  className="layout-name-input"
                />
                <button
                  className="save-layout-button"
                  onClick={() => saveCurrentLayout()}
                  disabled={!newLayoutName.trim()}
                >
                  Save Layout
                </button>
              </div>

              <button
                className="reset-layout-button"
                onClick={() => loadSavedLayout('Default')}
              >
                ↺ Reset to Default Layout
              </button>

              {savedLayouts.length > 1 && (
                <div className="saved-layouts-section">
                  <h4 className="settings-subheading">Saved Layouts</h4>
                  <div className="saved-layouts-list">
                    {savedLayouts.filter(name => name !== 'Default').map(layoutName => (
                      <button
                        key={layoutName}
                        className="saved-layout-button"
                        onClick={() => loadSavedLayout(layoutName)}
                      >
                        {layoutName}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="settings-footer">
          <button className="reset-button" onClick={resetSettings}>
            Reset All Settings
          </button>
          <div className="action-buttons">
            <button className="cancel-button" onClick={onClose}>
              Cancel
            </button>
            <button className="save-button" onClick={applySettings}>
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;
