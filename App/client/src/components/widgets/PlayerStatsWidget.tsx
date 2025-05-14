import React, { useState } from 'react';
import '../../styles/widgets/PlayerStatsWidget.css';

// Define tab types
type TabType = 'stats' | 'inventory' | 'abilities';

// Mock player stats data (would come from the server in a real implementation)
const mockPlayerStats = {
  hp: {
    current: 25,
    maximum: 30,
  },
  level: 3,
  experience: 2500,
  next_level_xp: 4000,
  armor_class: 15,
};

// Mock character data (would come from the server in a real implementation)
const mockCharacterData = {
  name: 'Thalion',
  race: 'Human',
  class: 'Fighter',
  level: 3,
  abilities: {
    strength: 16,
    dexterity: 14,
    constitution: 15,
    intelligence: 12,
    wisdom: 10,
    charisma: 13
  },
  equipment: [
    { name: 'Longsword', type: 'Weapon', details: '1d8 slashing' },
    { name: 'Chain Mail', type: 'Armor', details: 'AC 16' },
    { name: 'Shield', type: 'Armor', details: '+2 AC' },
    { name: 'Backpack', type: 'Gear', details: 'Contains adventuring gear' }
  ],
  spells: [],
  skills: {
    'Athletics': 5,
    'Intimidation': 3,
    'Perception': 2,
    'Survival': 2
  }
};

const PlayerStatsWidget: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('stats');
  
  // In a real implementation, these would come from the Socket context
  const playerStats = mockPlayerStats;
  const characterData = mockCharacterData;

  // Handle tab change
  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
  };

  // Render stats tab content
  const renderStatsTab = () => {
    if (!playerStats || !characterData) {
      return <p className="loading-text">Loading player stats...</p>;
    }

    return (
      <div className="stats-container">
        <div className="character-header">
          <h3 className="character-name">{characterData.name}</h3>
          <div className="character-details">
            <span className="character-race-class">{characterData.race} {characterData.class}</span>
            <span className="character-level">Level {characterData.level}</span>
          </div>
        </div>

        <div className="stat-row hp-row">
          <span className="stat-label">HP:</span>
          <div className="hp-bar-container">
            <div 
              className="hp-bar" 
              style={{ 
                width: `${(playerStats.hp.current / playerStats.hp.maximum) * 100}%`,
                backgroundColor: getHPColor(playerStats.hp.current, playerStats.hp.maximum)
              }}
            ></div>
            <span className="hp-text">{playerStats.hp.current}/{playerStats.hp.maximum}</span>
          </div>
        </div>

        <div className="stat-row xp-row">
          <span className="stat-label">XP:</span>
          <div className="xp-bar-container">
            <div 
              className="xp-bar" 
              style={{ 
                width: `${(playerStats.experience / playerStats.next_level_xp) * 100}%` 
              }}
            ></div>
            <span className="xp-text">{playerStats.experience}/{playerStats.next_level_xp}</span>
          </div>
        </div>

        <div className="stat-row">
          <span className="stat-label">Armor Class:</span>
          <span className="stat-value">{playerStats.armor_class}</span>
        </div>

        <div className="abilities-container">
          <h4>Abilities</h4>
          <div className="abilities-grid">
            <div className="ability">
              <span className="ability-label">STR</span>
              <span className="ability-value">{characterData.abilities.strength}</span>
              <span className="ability-modifier">{getAbilityModifier(characterData.abilities.strength)}</span>
            </div>
            <div className="ability">
              <span className="ability-label">DEX</span>
              <span className="ability-value">{characterData.abilities.dexterity}</span>
              <span className="ability-modifier">{getAbilityModifier(characterData.abilities.dexterity)}</span>
            </div>
            <div className="ability">
              <span className="ability-label">CON</span>
              <span className="ability-value">{characterData.abilities.constitution}</span>
              <span className="ability-modifier">{getAbilityModifier(characterData.abilities.constitution)}</span>
            </div>
            <div className="ability">
              <span className="ability-label">INT</span>
              <span className="ability-value">{characterData.abilities.intelligence}</span>
              <span className="ability-modifier">{getAbilityModifier(characterData.abilities.intelligence)}</span>
            </div>
            <div className="ability">
              <span className="ability-label">WIS</span>
              <span className="ability-value">{characterData.abilities.wisdom}</span>
              <span className="ability-modifier">{getAbilityModifier(characterData.abilities.wisdom)}</span>
            </div>
            <div className="ability">
              <span className="ability-label">CHA</span>
              <span className="ability-value">{characterData.abilities.charisma}</span>
              <span className="ability-modifier">{getAbilityModifier(characterData.abilities.charisma)}</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Render inventory tab content
  const renderInventoryTab = () => {
    if (!characterData) {
      return <p className="loading-text">Loading inventory...</p>;
    }

    return (
      <div className="inventory-container">
        <h4>Equipment</h4>
        {characterData.equipment.length > 0 ? (
          <ul className="equipment-list">
            {characterData.equipment.map((item, index) => (
              <li key={index} className="equipment-item">
                <span className="item-name">{item.name}</span>
                <span className="item-type">{item.type}</span>
                <span className="item-details">{item.details}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="empty-list">No equipment found.</p>
        )}
      </div>
    );
  };

  // Render abilities tab content
  const renderAbilitiesTab = () => {
    if (!characterData) {
      return <p className="loading-text">Loading abilities...</p>;
    }

    // Display class-specific abilities
    // This would be expanded based on the character's class
    return (
      <div className="abilities-container">
        <h4>Class Abilities</h4>
        {characterData.class === 'Fighter' && (
          <ul className="abilities-list">
            <li className="ability-item">
              <span className="ability-name">Second Wind</span>
              <p className="ability-description">Regain hit points equal to 1d10 + fighter level. Once per short rest.</p>
            </li>
            <li className="ability-item">
              <span className="ability-name">Action Surge</span>
              <p className="ability-description">Take an additional action on your turn. Once per short rest.</p>
            </li>
          </ul>
        )}
        
        {characterData.class === 'Wizard' && (
          <ul className="abilities-list">
            <li className="ability-item">
              <span className="ability-name">Arcane Recovery</span>
              <p className="ability-description">Recover spell slots during a short rest. Once per day.</p>
            </li>
          </ul>
        )}
        
        {characterData.class === 'Thief' && (
          <div className="thief-abilities">
            <h5>Thief Abilities</h5>
            <div className="thief-skills">
              <div className="thief-skill">
                <span className="skill-name">Pick Pockets</span>
                <span className="skill-value">35%</span>
              </div>
              <div className="thief-skill">
                <span className="skill-name">Open Locks</span>
                <span className="skill-value">30%</span>
              </div>
              <div className="thief-skill">
                <span className="skill-name">Find Traps</span>
                <span className="skill-value">25%</span>
              </div>
              <div className="thief-skill">
                <span className="skill-name">Move Silently</span>
                <span className="skill-value">30%</span>
              </div>
              <div className="thief-skill">
                <span className="skill-name">Hide in Shadows</span>
                <span className="skill-value">25%</span>
              </div>
              <div className="thief-skill">
                <span className="skill-name">Climb Walls</span>
                <span className="skill-value">85%</span>
              </div>
            </div>
          </div>
        )}
        
        {!['Fighter', 'Wizard', 'Thief'].includes(characterData.class) && (
          <p className="empty-list">No class-specific abilities found.</p>
        )}
      </div>
    );
  };

  // Helper function to get HP color based on current/max ratio
  const getHPColor = (current: number, max: number): string => {
    const ratio = current / max;
    if (ratio > 0.6) return '#4caf50'; // Green
    if (ratio > 0.3) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  // Helper function to calculate ability modifier
  const getAbilityModifier = (score: number): string => {
    const modifier = Math.floor((score - 10) / 2);
    return modifier >= 0 ? `+${modifier}` : `${modifier}`;
  };

  return (
    <div className="player-stats-widget">
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => handleTabChange('stats')}
        >
          Stats
        </button>
        <button 
          className={`tab ${activeTab === 'inventory' ? 'active' : ''}`}
          onClick={() => handleTabChange('inventory')}
        >
          Inventory
        </button>
        <button 
          className={`tab ${activeTab === 'abilities' ? 'active' : ''}`}
          onClick={() => handleTabChange('abilities')}
        >
          Abilities
        </button>
      </div>
      
      <div className="tab-content">
        {activeTab === 'stats' && renderStatsTab()}
        {activeTab === 'inventory' && renderInventoryTab()}
        {activeTab === 'abilities' && renderAbilitiesTab()}
      </div>
    </div>
  );
};

export default PlayerStatsWidget;
