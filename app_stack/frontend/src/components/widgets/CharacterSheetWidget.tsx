import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useSocket } from '../../context/SocketContext';
import { useTheme } from '../../context/ThemeContext';
import { WidgetProps, WidgetCategory } from '../../types/widget';
import withWidget from './withWidget';

const CharacterSheetContainer = styled.div`
  height: 100%;
  overflow-y: auto;
`;

const TabsContainer = styled.div`
  display: flex;
  border-bottom: 1px solid var(--${props => props.theme}-border);
  margin-bottom: var(--spacing-md);
`;

const Tab = styled.button<{ active: boolean }>`
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: ${props => props.active
    ? `var(--${props.theme}-primary)`
    : 'transparent'};
  color: ${props => props.active
    ? (props.theme === 'dark' ? 'black' : 'white')
    : `var(--${props.theme}-text-primary)`};
  border: none;
  border-bottom: 2px solid ${props => props.active
    ? `var(--${props.theme}-primary)`
    : 'transparent'};
  cursor: pointer;
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast) ease;

  &:hover {
    background-color: ${props => props.active
      ? `var(--${props.theme}-primary)`
      : props.theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'};
  }
`;

const TabContent = styled.div<{ active: boolean }>`
  display: ${props => props.active ? 'block' : 'none'};
`;

const CharacterHeader = styled.div`
  margin-bottom: var(--spacing-md);
`;

const CharacterName = styled.h3`
  margin: 0;
  font-size: var(--font-size-xl);
  color: var(--${props => props.theme}-primary);
`;

const CharacterSubtitle = styled.div`
  font-size: var(--font-size-sm);
  color: var(--${props => props.theme}-text-secondary);
`;

const AbilitiesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
`;

const AbilityBox = styled.div`
  background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)'};
  border: 1px solid var(--${props => props.theme}-border);
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-sm);
  text-align: center;
`;

const AbilityName = styled.div`
  font-size: var(--font-size-xs);
  color: var(--${props => props.theme}-text-secondary);
  margin-bottom: var(--spacing-xs);
`;

const AbilityScore = styled.div`
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--${props => props.theme}-primary);
`;

const AbilityMod = styled.div`
  font-size: var(--font-size-sm);
  color: var(--${props => props.theme}-text-primary);
`;

const SectionTitle = styled.h4`
  margin-top: var(--spacing-lg);
  margin-bottom: var(--spacing-sm);
  font-size: var(--font-size-md);
  color: var(--${props => props.theme}-primary);
  border-bottom: 1px solid var(--${props => props.theme}-border);
  padding-bottom: var(--spacing-xs);
`;

const EquipmentList = styled.ul`
  list-style-type: none;
  padding: 0;
  margin: 0;
`;

const EquipmentItem = styled.li`
  padding: var(--spacing-sm);
  border-bottom: 1px solid var(--${props => props.theme}-border);
  display: flex;
  justify-content: space-between;
  align-items: center;

  &:last-child {
    border-bottom: none;
  }
`;

const ItemName = styled.span`
  font-weight: 500;
`;

const ItemDetails = styled.span`
  font-size: var(--font-size-sm);
  color: var(--${props => props.theme}-text-secondary);
`;

interface Character {
  name: string;
  race: string;
  class: string;
  level: number;
  abilities: {
    strength: number;
    dexterity: number;
    constitution: number;
    intelligence: number;
    wisdom: number;
    charisma: number;
  };
  equipment: Array<{
    name: string;
    type: string;
    details: string;
  }>;
  spells: string[];
  skills: Record<string, number>;
}

// Default character data for in-memory mode
const defaultCharacter: Character = {
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

interface CharacterSheetConfig {
  showAbilities: boolean;
  showEquipment: boolean;
  showSkills: boolean;
  showSpells: boolean;
  defaultTab: string;
}

const defaultConfig: CharacterSheetConfig = {
  showAbilities: true,
  showEquipment: true,
  showSkills: true,
  showSpells: true,
  defaultTab: 'abilities'
};

const CharacterSheetWidget: React.FC<WidgetProps> = ({ id, config }) => {
  const { theme } = useTheme();
  const { socket, isConnected } = useSocket();
  const widgetConfig = { ...defaultConfig, ...config } as CharacterSheetConfig;
  const [activeTab, setActiveTab] = useState(widgetConfig.defaultTab);
  const [character, setCharacter] = useState<Character>(defaultCharacter);

  // Listen for character updates from server
  useEffect(() => {
    if (socket && isConnected) {
      socket.on('character:update', (updatedCharacter: Character) => {
        setCharacter(updatedCharacter);
      });

      // Request character data
      socket.emit('character:request');

      return () => {
        socket.off('character:update');
      };
    }
  }, [socket, isConnected]);

  // Calculate ability modifiers
  const getAbilityModifier = (score: number) => {
    const modifier = Math.floor((score - 10) / 2);
    return modifier >= 0 ? `+${modifier}` : modifier.toString();
  };

  return (
    <CharacterSheetContainer>
      <CharacterHeader>
        <CharacterName theme={theme}>{character.name}</CharacterName>
        <CharacterSubtitle theme={theme}>
          Level {character.level} {character.race} {character.class}
        </CharacterSubtitle>
      </CharacterHeader>

      <TabsContainer theme={theme}>
        {widgetConfig.showAbilities && (
          <Tab
            active={activeTab === 'abilities'}
            onClick={() => setActiveTab('abilities')}
            theme={theme}
          >
            Abilities
          </Tab>
        )}
        {widgetConfig.showEquipment && (
          <Tab
            active={activeTab === 'equipment'}
            onClick={() => setActiveTab('equipment')}
            theme={theme}
          >
            Equipment
          </Tab>
        )}
        {widgetConfig.showSkills && (
          <Tab
            active={activeTab === 'skills'}
            onClick={() => setActiveTab('skills')}
            theme={theme}
          >
            Skills
          </Tab>
        )}
        {widgetConfig.showSpells && (
          <Tab
            active={activeTab === 'spells'}
            onClick={() => setActiveTab('spells')}
            theme={theme}
          >
            Spells
          </Tab>
        )}
      </TabsContainer>

      <TabContent active={activeTab === 'abilities'}>
        <AbilitiesGrid>
          {Object.entries(character.abilities).map(([ability, score]) => (
            <AbilityBox key={ability} theme={theme}>
              <AbilityName theme={theme}>{ability.toUpperCase()}</AbilityName>
              <AbilityScore theme={theme}>{score}</AbilityScore>
              <AbilityMod theme={theme}>{getAbilityModifier(score)}</AbilityMod>
            </AbilityBox>
          ))}
        </AbilitiesGrid>
      </TabContent>

      <TabContent active={activeTab === 'equipment'}>
        <SectionTitle theme={theme}>Weapons & Armor</SectionTitle>
        <EquipmentList>
          {character.equipment
            .filter(item => item.type === 'Weapon' || item.type === 'Armor')
            .map((item, index) => (
              <EquipmentItem key={index} theme={theme}>
                <ItemName>{item.name}</ItemName>
                <ItemDetails theme={theme}>{item.details}</ItemDetails>
              </EquipmentItem>
            ))}
        </EquipmentList>

        <SectionTitle theme={theme}>Gear & Items</SectionTitle>
        <EquipmentList>
          {character.equipment
            .filter(item => item.type === 'Gear')
            .map((item, index) => (
              <EquipmentItem key={index} theme={theme}>
                <ItemName>{item.name}</ItemName>
                <ItemDetails theme={theme}>{item.details}</ItemDetails>
              </EquipmentItem>
            ))}
        </EquipmentList>
      </TabContent>

      <TabContent active={activeTab === 'skills'}>
        <SectionTitle theme={theme}>Skills</SectionTitle>
        <EquipmentList>
          {Object.entries(character.skills).map(([skill, bonus]) => (
            <EquipmentItem key={skill} theme={theme}>
              <ItemName>{skill}</ItemName>
              <ItemDetails theme={theme}>+{bonus}</ItemDetails>
            </EquipmentItem>
          ))}
        </EquipmentList>
      </TabContent>

      <TabContent active={activeTab === 'spells'}>
        {character.spells && character.spells.length > 0 ? (
          <>
            <SectionTitle theme={theme}>Spells</SectionTitle>
            <EquipmentList>
              {character.spells.map((spell, index) => (
                <EquipmentItem key={index} theme={theme}>
                  <ItemName>{spell}</ItemName>
                </EquipmentItem>
              ))}
            </EquipmentList>
          </>
        ) : (
          <div style={{ textAlign: 'center', padding: 'var(--spacing-lg)', color: `var(--${theme}-text-secondary)` }}>
            This character doesn't know any spells.
          </div>
        )}
      </TabContent>
    </CharacterSheetContainer>
  );
};

export default withWidget(CharacterSheetWidget, {
  metadata: {
    name: 'Character Sheet',
    description: 'Display character information',
    category: WidgetCategory.CHARACTER,
    icon: '📝',
    defaultSize: {
      w: 8,
      h: 4,
    },
    minW: 4,
    minH: 3,
  },
  defaultConfig,
});
