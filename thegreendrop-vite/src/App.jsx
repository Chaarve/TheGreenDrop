import React, { useState } from "react";
import WaterPredictionForm from "./WaterPredictionForm";
import Dashboard from "./Dashboard";
import WeatherAlerts from "./WeatherAlerts";
import "./App.css";

function App() {
  const [currentView, setCurrentView] = useState('prediction');
  const [selectedLocation, setSelectedLocation] = useState(null);

  const handleLocationSelect = (location) => {
    setSelectedLocation(location);
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'alerts':
        return selectedLocation ? (
          <WeatherAlerts 
            latitude={selectedLocation.latitude} 
            longitude={selectedLocation.longitude} 
          />
        ) : (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>📍</div>
            <p>Please make a prediction first to view weather alerts for your location.</p>
            <button 
              onClick={() => setCurrentView('prediction')}
              style={{ 
                padding: '10px 20px', 
                background: '#3498db', 
                color: 'white', 
                border: 'none', 
                borderRadius: '5px', 
                cursor: 'pointer',
                marginTop: '10px'
              }}
            >
              Go to Prediction
            </button>
          </div>
        );
      case 'prediction':
      default:
        return <WaterPredictionForm onLocationSelect={handleLocationSelect} />;
    }
  };

  return (
    <div className="App">
      {/* Navigation */}
      <nav style={{ 
        background: '#2c3e50', 
        padding: '15px 0', 
        marginBottom: '20px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'center', gap: '20px' }}>
          <button
            onClick={() => setCurrentView('prediction')}
            style={{
              padding: '10px 20px',
              background: currentView === 'prediction' ? '#3498db' : 'transparent',
              color: 'white',
              border: '1px solid #3498db',
              borderRadius: '5px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
            🌧️ Prediction
          </button>
          <button
            onClick={() => setCurrentView('dashboard')}
            style={{
              padding: '10px 20px',
              background: currentView === 'dashboard' ? '#3498db' : 'transparent',
              color: 'white',
              border: '1px solid #3498db',
              borderRadius: '5px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
            📊 Dashboard
          </button>
          <button
            onClick={() => setCurrentView('alerts')}
            style={{
              padding: '10px 20px',
              background: currentView === 'alerts' ? '#3498db' : 'transparent',
              color: 'white',
              border: '1px solid #3498db',
              borderRadius: '5px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
            🌤️ Weather Alerts
          </button>
        </div>
      </nav>

      {/* Main Content */}
      {renderCurrentView()}
    </div>
  );
}

export default App;