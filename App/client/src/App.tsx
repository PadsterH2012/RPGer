import React from 'react';
import { useTheme } from './context/ThemeContext';
import RPG_DashboardComponent from './components/RPG_Dashboard';

const App: React.FC = () => {
  const { theme } = useTheme();

  return (
    <div className={`app ${theme}`}>
      <RPG_DashboardComponent />
    </div>
  );
};

export default App;
