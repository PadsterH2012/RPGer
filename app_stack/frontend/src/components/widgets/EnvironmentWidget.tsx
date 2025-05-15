import React from 'react';
import '../../styles/widgets/EnvironmentWidget.css';

// Mock environment data (would come from the server in a real implementation)
const mockEnvironmentData = {
  location: 'Forgotten Forest',
  time: 'Dusk',
  weather: 'Light Rain',
  description: 'The ancient trees of the Forgotten Forest loom overhead, their branches swaying gently in the evening breeze. The light rain creates a soothing patter on the leaves above, and the forest floor is damp beneath your feet. The path ahead is shrouded in mist, and you can hear distant sounds of wildlife preparing for the night.',
  dangers: 'Medium',
  visibility: 'Poor',
};

const EnvironmentWidget: React.FC = () => {
  // In a real implementation, this would use the Socket context to get real-time data
  const environmentData = mockEnvironmentData;
  
  return (
    <div className="environment-widget">
      <div className="environment-header">
        <div className="environment-location">{environmentData.location}</div>
        <div className="environment-time-weather">
          <span className="environment-time">{environmentData.time}</span>
          <span className="environment-weather">{environmentData.weather}</span>
        </div>
      </div>
      
      <div className="environment-description">
        <p>{environmentData.description}</p>
      </div>
      
      <div className="environment-conditions">
        <div className="condition">
          <span className="condition-label">Danger Level:</span>
          <span className={`condition-value danger-${environmentData.dangers.toLowerCase()}`}>
            {environmentData.dangers}
          </span>
        </div>
        <div className="condition">
          <span className="condition-label">Visibility:</span>
          <span className={`condition-value visibility-${environmentData.visibility.toLowerCase()}`}>
            {environmentData.visibility}
          </span>
        </div>
      </div>
    </div>
  );
};

export default EnvironmentWidget;
