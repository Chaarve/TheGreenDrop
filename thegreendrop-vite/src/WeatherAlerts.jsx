import React, { useState, useEffect } from "react";
import axios from "axios";

export default function WeatherAlerts({ latitude, longitude }) {
  const [alerts, setAlerts] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [monsoonAnalysis, setMonsoonAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (latitude && longitude) {
      fetchWeatherAlerts();
      fetchForecast();
      fetchMonsoonAnalysis();
    }
  }, [latitude, longitude]);

  const fetchWeatherAlerts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/weather/alerts?lat=${latitude}&lon=${longitude}`);
      setAlerts(response.data.alerts || []);
    } catch (error) {
      console.error("Error fetching weather alerts:", error);
      setError("Failed to fetch weather alerts");
    } finally {
      setLoading(false);
    }
  };

  const fetchForecast = async () => {
    try {
      const response = await axios.get(`/api/weather/forecast?lat=${latitude}&lon=${longitude}`);
      setForecast(response.data);
    } catch (error) {
      console.error("Error fetching forecast:", error);
    }
  };

  const fetchMonsoonAnalysis = async () => {
    try {
      const response = await axios.get(`/api/weather/monsoon-analysis?lat=${latitude}&lon=${longitude}`);
      setMonsoonAnalysis(response.data);
    } catch (error) {
      console.error("Error fetching monsoon analysis:", error);
    }
  };

  const getAlertIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'warning': return '⚠️';
      case 'alert': return '🚨';
      case 'storm': return '⛈️';
      case 'rain': return '🌧️';
      case 'flood': return '🌊';
      default: return '📢';
    }
  };

  const getAlertColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'high': return '#e74c3c';
      case 'medium': return '#f39c12';
      case 'low': return '#f1c40f';
      default: return '#3498db';
    }
  };

  if (!latitude || !longitude) {
    return (
      <div style={{ textAlign: 'center', padding: '20px', color: '#7f8c8d' }}>
        <div style={{ fontSize: '24px', marginBottom: '10px' }}>📍</div>
        <p>Enter coordinates to view weather alerts</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h2 style={{ color: '#2c3e50', marginBottom: '10px' }}>🌤️ Weather Alerts & Forecast</h2>
        <p style={{ color: '#7f8c8d' }}>Location: {latitude.toFixed(4)}, {longitude.toFixed(4)}</p>
      </div>

      {/* Weather Alerts */}
      <div style={{ background: '#f8f9fa', padding: '25px', borderRadius: '10px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)', marginBottom: '20px' }}>
        <h3 style={{ color: '#2c3e50', marginBottom: '20px' }}>🚨 Weather Alerts</h3>
        
        {loading ? (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <div style={{ fontSize: '24px', marginBottom: '10px' }}>⏳</div>
            <p>Loading alerts...</p>
          </div>
        ) : error ? (
          <div style={{ textAlign: 'center', padding: '20px', color: '#e74c3c' }}>
            <div style={{ fontSize: '24px', marginBottom: '10px' }}>❌</div>
            <p>{error}</p>
            <button 
              onClick={fetchWeatherAlerts}
              style={{ 
                padding: '8px 16px', 
                background: '#3498db', 
                color: 'white', 
                border: 'none', 
                borderRadius: '4px', 
                cursor: 'pointer',
                marginTop: '10px'
              }}
            >
              Retry
            </button>
          </div>
        ) : alerts.length > 0 ? (
          <div style={{ display: 'grid', gap: '15px' }}>
            {alerts.map((alert, index) => (
              <div 
                key={index} 
                style={{ 
                  background: 'white', 
                  padding: '15px', 
                  borderRadius: '8px', 
                  borderLeft: `4px solid ${getAlertColor(alert.level)}`,
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '20px', marginRight: '10px' }}>
                    {getAlertIcon(alert.type)}
                  </span>
                  <strong style={{ color: getAlertColor(alert.level) }}>
                    {alert.type || 'Weather Alert'}
                  </strong>
                  <span style={{ 
                    marginLeft: 'auto', 
                    fontSize: '12px', 
                    color: '#666',
                    background: '#f8f9fa',
                    padding: '2px 8px',
                    borderRadius: '12px'
                  }}>
                    {alert.level || 'Normal'}
                  </span>
                </div>
                <p style={{ margin: '0', color: '#555' }}>{alert.message || 'No additional details available'}</p>
                {alert.timestamp && (
                  <p style={{ margin: '8px 0 0 0', fontSize: '12px', color: '#999' }}>
                    {new Date(alert.timestamp).toLocaleString()}
                  </p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '20px', color: '#27ae60' }}>
            <div style={{ fontSize: '24px', marginBottom: '10px' }}>✅</div>
            <p>No active weather alerts for this location</p>
          </div>
        )}
      </div>

      {/* 7-Day Forecast */}
      {forecast && forecast.forecast_days && forecast.forecast_days.length > 0 && (
        <div style={{ background: '#f8f9fa', padding: '25px', borderRadius: '10px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)', marginBottom: '20px' }}>
          <h3 style={{ color: '#2c3e50', marginBottom: '20px' }}>📅 7-Day Forecast</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '15px' }}>
            {forecast.forecast_days.map((day, index) => (
              <div 
                key={index} 
                style={{ 
                  background: 'white', 
                  padding: '15px', 
                  borderRadius: '8px', 
                  textAlign: 'center',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                }}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '8px', color: '#2c3e50' }}>
                  {day.date || `Day ${index + 1}`}
                </div>
                <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>
                  {day.max_temp_c}°/{day.min_temp_c}°
                </div>
                <div style={{ fontSize: '12px', color: '#3498db', marginBottom: '5px' }}>
                  {day.rainfall_mm}mm
                </div>
                <div style={{ fontSize: '12px', color: '#7f8c8d' }}>
                  {day.weather_condition || 'Clear'}
                </div>
              </div>
            ))}
          </div>
          
          {forecast.forecast_total_rainfall_mm > 0 && (
            <div style={{ marginTop: '20px', padding: '15px', background: '#e3f2fd', borderRadius: '8px' }}>
              <div style={{ textAlign: 'center' }}>
                <strong>Total Forecast Rainfall:</strong> {forecast.forecast_total_rainfall_mm}mm
                <br />
                <strong>Rainy Days:</strong> {forecast.forecast_rainy_days} out of {forecast.forecast_period_days}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Monsoon Analysis */}
      {monsoonAnalysis && (
        <div style={{ background: '#f8f9fa', padding: '25px', borderRadius: '10px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
          <h3 style={{ color: '#2c3e50', marginBottom: '20px' }}>🌧️ Monsoon Analysis</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
            {/* Monsoon Intensity */}
            {monsoonAnalysis.monsoon_intensity && (
              <div style={{ background: 'white', padding: '15px', borderRadius: '8px' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#2980b9' }}>Monsoon Intensity</h4>
                <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#2980b9' }}>
                  {monsoonAnalysis.monsoon_intensity.monsoon_intensity || 'Moderate'}
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>
                  Score: {((monsoonAnalysis.monsoon_intensity.intensity_score || 0.5) * 100).toFixed(0)}%
                </div>
              </div>
            )}

            {/* Rainfall Distribution */}
            {monsoonAnalysis.rainfall_distribution && (
              <div style={{ background: 'white', padding: '15px', borderRadius: '8px' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#27ae60' }}>Rainfall Distribution</h4>
                <div style={{ fontSize: '14px', marginBottom: '5px' }}>
                  Annual: {monsoonAnalysis.rainfall_distribution.annual_rainfall_mm}mm
                </div>
                <div style={{ fontSize: '14px', marginBottom: '5px' }}>
                  Max Daily: {monsoonAnalysis.rainfall_distribution.max_daily_rainfall_mm}mm
                </div>
                <div style={{ fontSize: '14px' }}>
                  Rainy Days: {monsoonAnalysis.rainfall_distribution.rainy_days_count}
                </div>
              </div>
            )}

            {/* Recharge Potential */}
            {monsoonAnalysis.recharge_potential && (
              <div style={{ background: 'white', padding: '15px', borderRadius: '8px' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#f39c12' }}>Recharge Potential</h4>
                <div style={{ fontSize: '14px', marginBottom: '5px' }}>
                  Infiltration: {((monsoonAnalysis.recharge_potential.infiltration_potential || 0) * 100).toFixed(1)}%
                </div>
                <div style={{ fontSize: '14px', marginBottom: '5px' }}>
                  Efficiency: {((monsoonAnalysis.recharge_potential.recharge_efficiency || 0) * 100).toFixed(1)}%
                </div>
                <div style={{ fontSize: '14px' }}>
                  Evaporation: {monsoonAnalysis.recharge_potential.evaporation_rate_mmday}mm/day
                </div>
              </div>
            )}

            {/* Seasonal Patterns */}
            {monsoonAnalysis.seasonal_patterns && (
              <div style={{ background: 'white', padding: '15px', borderRadius: '8px' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#9b59b6' }}>Seasonal Patterns</h4>
                <div style={{ fontSize: '14px', marginBottom: '5px' }}>
                  Season: {monsoonAnalysis.seasonal_patterns.current_season || 'Unknown'}
                </div>
                <div style={{ fontSize: '14px' }}>
                  Factor: {monsoonAnalysis.seasonal_patterns.recharge_factor || 1.0}x
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
