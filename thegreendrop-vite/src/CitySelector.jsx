import React, { useState, useEffect } from "react";
import axios from "axios";

export default function CitySelector({ onCitySelect, selectedCity }) {
  const [cities, setCities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCities();
  }, []);

  const fetchCities = async () => {
    try {
      setLoading(true);
      const response = await axios.get("/api/weather/cities");
      setCities(response.data.cities || []);
    } catch (error) {
      console.error("Error fetching cities:", error);
      setError("Failed to fetch cities");
    } finally {
      setLoading(false);
    }
  };

  const handleCityChange = (event) => {
    const cityId = parseInt(event.target.value);
    const city = cities.find(c => c.id === cityId);
    if (city && onCitySelect) {
      onCitySelect(city);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <div style={{ fontSize: '24px', marginBottom: '10px' }}>⏳</div>
        <p>Loading cities...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '20px', color: '#e74c3c' }}>
        <div style={{ fontSize: '24px', marginBottom: '10px' }}>❌</div>
        <p>{error}</p>
        <button 
          onClick={fetchCities}
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
    );
  }

  return (
    <div style={{ marginBottom: '20px' }}>
      <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#2c3e50' }}>
        🏙️ Select City (Optional)
      </label>
      <select
        value={selectedCity?.id || ''}
        onChange={handleCityChange}
        style={{
          width: '100%',
          padding: '10px',
          border: '1px solid #ddd',
          borderRadius: '6px',
          fontSize: '14px',
          background: 'white',
          cursor: 'pointer'
        }}
      >
        <option value="">Choose a city for enhanced weather data...</option>
        {cities.map((city) => (
          <option key={city.id} value={city.id}>
            {city.name}, {city.state}
          </option>
        ))}
      </select>
      {selectedCity && (
        <div style={{ 
          marginTop: '8px', 
          padding: '8px', 
          background: '#e8f4fd', 
          borderRadius: '4px', 
          fontSize: '12px', 
          color: '#2980b9' 
        }}>
          ✅ Selected: {selectedCity.name}, {selectedCity.state} (ID: {selectedCity.id})
        </div>
      )}
    </div>
  );
}
