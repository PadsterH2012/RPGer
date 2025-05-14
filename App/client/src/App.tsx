import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { useTheme } from './context/ThemeContext';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import NewDashboard from './pages/NewDashboard';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

const App: React.FC = () => {
  const { theme } = useTheme();
  
  return (
    <div className={`app ${theme}`}>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="new-dashboard" element={<NewDashboard />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </div>
  );
};

export default App;
