import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { ThemeProvider } from './context/ThemeContext';
import { SocketProvider } from './context/SocketContext';
import { WidgetProvider } from './context/WidgetContext';
import './styles/global.css';
import reportWebVitals from './reportWebVitals';

// Import widgets to register them
import './components/widgets/TextWidget';
import './components/widgets/TableWidget';
import './components/widgets/ClockWidget';
import './components/widgets/CountdownWidget';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <SocketProvider>
          <WidgetProvider>
            <App />
          </WidgetProvider>
        </SocketProvider>
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
