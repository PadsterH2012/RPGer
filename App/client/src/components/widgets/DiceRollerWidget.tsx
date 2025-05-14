import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useSocket } from '../../context/SocketContext';
import { useTheme } from '../../context/ThemeContext';
import { WidgetProps, WidgetCategory } from '../../types/widget';
import withWidget from './withWidget';

const DiceRollerContainer = styled.div`
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const DiceControls = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
`;

const DiceButton = styled.button<{ active?: boolean }>`
  background-color: ${props => props.active
    ? `var(--${props.theme}-primary)`
    : props.theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'};
  color: ${props => props.active
    ? (props.theme === 'dark' ? 'black' : 'white')
    : `var(--${props.theme}-text-primary)`};
  border: 1px solid ${props => props.active
    ? `var(--${props.theme}-primary)`
    : `var(--${props.theme}-border)`};
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-sm);
  font-size: var(--font-size-md);
  font-weight: ${props => props.active ? '700' : '400'};
  cursor: pointer;
  transition: all var(--transition-fast) ease;

  &:hover {
    background-color: ${props => props.active
      ? `var(--${props.theme}-primary-variant)`
      : props.theme === 'dark' ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)'};
  }
`;

const QuantityControls = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: var(--spacing-md);
`;

const QuantityLabel = styled.span`
  margin-right: var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--${props => props.theme}-text-secondary);
`;

const QuantityButton = styled.button`
  background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'};
  color: var(--${props => props.theme}-text-primary);
  border: 1px solid var(--${props => props.theme}-border);
  border-radius: var(--border-radius-sm);
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-md);
  cursor: pointer;
  transition: background-color var(--transition-fast) ease;

  &:hover {
    background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)'};
  }
`;

const QuantityValue = styled.span`
  margin: 0 var(--spacing-md);
  font-size: var(--font-size-md);
  font-weight: 500;
  min-width: 20px;
  text-align: center;
`;

const RollButton = styled.button`
  background-color: var(--${props => props.theme}-primary);
  color: ${props => props.theme === 'dark' ? 'black' : 'white'};
  border: none;
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-md);
  font-size: var(--font-size-md);
  font-weight: 700;
  cursor: pointer;
  transition: background-color var(--transition-fast) ease;
  margin-bottom: var(--spacing-md);

  &:hover {
    background-color: var(--${props => props.theme}-primary-variant);
  }
`;

const ResultsContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  border: 1px solid var(--${props => props.theme}-border);
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-sm);
  background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)'};
`;

const RollResult = styled.div<{ isNew?: boolean }>`
  padding: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  background-color: ${props => props.isNew
    ? (props.theme === 'dark' ? 'rgba(187, 134, 252, 0.1)' : 'rgba(187, 134, 252, 0.05)')
    : 'transparent'};
  border-left: 3px solid ${props => props.isNew
    ? 'var(--dark-primary)'
    : props.theme === 'dark' ? 'var(--dark-border)' : 'var(--light-border)'};
  transition: background-color var(--transition-normal) ease;
`;

const RollTime = styled.div`
  font-size: var(--font-size-xs);
  color: var(--${props => props.theme}-text-secondary);
  margin-bottom: var(--spacing-xs);
`;

const RollFormula = styled.div`
  font-size: var(--font-size-sm);
  font-weight: 500;
  margin-bottom: var(--spacing-xs);
`;

const RollTotal = styled.div`
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--${props => props.theme}-primary);
`;

const RollDetails = styled.div`
  font-size: var(--font-size-xs);
  color: var(--${props => props.theme}-text-secondary);
  margin-top: var(--spacing-xs);
`;

interface DiceRoll {
  id: string;
  formula: string;
  quantity: number;
  sides: number;
  results: number[];
  total: number;
  timestamp: string;
}

interface DiceRollerConfig {
  defaultDice: number;
  defaultQuantity: number;
  maxQuantity: number;
  availableDice: number[];
  showHistory: boolean;
  maxHistory: number;
}

const defaultConfig: DiceRollerConfig = {
  defaultDice: 20,
  defaultQuantity: 1,
  maxQuantity: 10,
  availableDice: [4, 6, 8, 10, 12, 20, 100],
  showHistory: true,
  maxHistory: 10
};

const DiceRollerWidget: React.FC<WidgetProps> = ({ id, config }) => {
  const { theme } = useTheme();
  const { socket, isConnected } = useSocket();
  const widgetConfig = { ...defaultConfig, ...config } as DiceRollerConfig;

  const [selectedDice, setSelectedDice] = useState(widgetConfig.defaultDice);
  const [quantity, setQuantity] = useState(widgetConfig.defaultQuantity);
  const [rolls, setRolls] = useState<DiceRoll[]>([]);
  const [newRollId, setNewRollId] = useState<string | null>(null);

  // Listen for dice rolls from server
  useEffect(() => {
    if (socket && isConnected) {
      socket.on('dice:roll', (roll: DiceRoll) => {
        setRolls(prevRolls => [roll, ...prevRolls.slice(0, 9)]);
        setNewRollId(roll.id);

        // Clear "new" status after animation
        setTimeout(() => {
          setNewRollId(null);
        }, 3000);
      });

      return () => {
        socket.off('dice:roll');
      };
    }
  }, [socket, isConnected]);

  const handleDiceSelect = (sides: number) => {
    setSelectedDice(sides);
  };

  const handleQuantityChange = (delta: number) => {
    const newQuantity = Math.max(1, Math.min(widgetConfig.maxQuantity, quantity + delta));
    setQuantity(newQuantity);
  };

  const rollDice = () => {
    const results: number[] = [];
    let total = 0;

    for (let i = 0; i < quantity; i++) {
      const result = Math.floor(Math.random() * selectedDice) + 1;
      results.push(result);
      total += result;
    }

    const roll: DiceRoll = {
      id: Date.now().toString(),
      formula: `${quantity}d${selectedDice}`,
      quantity,
      sides: selectedDice,
      results,
      total,
      timestamp: new Date().toLocaleTimeString(),
    };

    // Add to local state
    setRolls(prevRolls => [roll, ...prevRolls.slice(0, widgetConfig.maxHistory - 1)]);
    setNewRollId(roll.id);

    // Clear "new" status after animation
    setTimeout(() => {
      setNewRollId(null);
    }, 3000);

    // Send to server if connected
    if (socket && isConnected) {
      socket.emit('dice:roll', roll);
    }
  };

  return (
    <DiceRollerContainer>
      <DiceControls>
        {widgetConfig.availableDice.map(sides => (
          <DiceButton
            key={sides}
            active={selectedDice === sides}
            onClick={() => handleDiceSelect(sides)}
            theme={theme}
          >
            d{sides}
          </DiceButton>
        ))}
      </DiceControls>

      <QuantityControls>
        <QuantityLabel theme={theme}>Quantity:</QuantityLabel>
        <QuantityButton onClick={() => handleQuantityChange(-1)} theme={theme}>-</QuantityButton>
        <QuantityValue>{quantity}</QuantityValue>
        <QuantityButton onClick={() => handleQuantityChange(1)} theme={theme}>+</QuantityButton>
      </QuantityControls>

      <RollButton onClick={rollDice} theme={theme}>
        Roll {quantity}d{selectedDice}
      </RollButton>

      {widgetConfig.showHistory && (
        <ResultsContainer theme={theme}>
          {rolls.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 'var(--spacing-md)', color: `var(--${theme}-text-secondary)` }}>
              No dice rolls yet
            </div>
          ) : (
            rolls.map(roll => (
              <RollResult key={roll.id} isNew={roll.id === newRollId} theme={theme}>
                <RollTime theme={theme}>{roll.timestamp}</RollTime>
                <RollFormula>{roll.formula}</RollFormula>
                <RollTotal theme={theme}>{roll.total}</RollTotal>
                <RollDetails theme={theme}>
                  [{roll.results.join(', ')}]
                </RollDetails>
              </RollResult>
            ))
          )}
        </ResultsContainer>
      )}
    </DiceRollerContainer>
  );
};

export default withWidget(DiceRollerWidget, {
  metadata: {
    name: 'Dice Roller',
    description: 'Roll virtual dice for your game',
    category: WidgetCategory.UTILITY,
    icon: '🎲',
    defaultSize: {
      w: 4,
      h: 3,
    },
    minW: 3,
    minH: 2,
  },
  defaultConfig,
});
