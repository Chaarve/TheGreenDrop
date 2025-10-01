import React, { useState, useEffect } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import CitySelector from "./CitySelector";

// Define your form fields dynamically - simplified for better UX
const formFields = [
  { name: "latitude", label: "Latitude", type: "number", step: "any", required: true },
  { name: "longitude", label: "Longitude", type: "number", step: "any", required: true },
  { name: "roof_area_m2", label: "Roof Area (m²)", type: "number", step: "any", required: true },
  { name: "roof_type", label: "Roof Type", type: "select", options: ["Concrete", "Metal", "Tile"], required: true },
  { name: "available_space_m2", label: "Available Space (m²)", type: "number", step: "any" },
  { name: "elevation_m", label: "Elevation (m)", type: "number", step: "any" },
  { name: "clay_pct", label: "Clay (%)", type: "number", step: "any" },
  { name: "sand_pct", label: "Sand (%)", type: "number", step: "any" },
  { name: "silt_pct", label: "Silt (%)", type: "number", step: "any" },
  { name: "infiltration_rate_mmhr", label: "Infiltration Rate (mm/hr)", type: "number", step: "any" },
  { name: "runoff_coefficient", label: "Runoff Coefficient", type: "number", step: "any" }
];

// Set initial values dynamically
const initialForm = {};
formFields.forEach(field => {
  if (field.type === "select") {
    initialForm[field.name] = field.options[0];
  } else {
    initialForm[field.name] = "";
  }
});

export default function WaterPredictionForm({ onLocationSelect }) {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [selectedCity, setSelectedCity] = useState(null);

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setForm({
            ...form,
            latitude: position.coords.latitude.toFixed(6),
            longitude: position.coords.longitude.toFixed(6)
          });
        },
        (error) => {
          console.error("Error getting location:", error);
        }
      );
    }
  };

  const fetchWeatherData = async (lat, lon, cityId = null) => {
    try {
      const url = cityId 
        ? `/api/weather?lat=${lat}&lon=${lon}&city_id=${cityId}`
        : `/api/weather?lat=${lat}&lon=${lon}`;
      const response = await axios.get(url);
      setWeatherData(response.data);
    } catch (error) {
      console.error("Error fetching weather data:", error);
      // Try to get recharge metrics as fallback
      try {
        const rechargeResponse = await axios.get(`/api/weather/recharge-metrics?lat=${lat}&lon=${lon}`);
        setWeatherData(rechargeResponse.data);
      } catch (fallbackError) {
        console.error("Error fetching recharge metrics:", fallbackError);
      }
    }
  };

  useEffect(() => {
    if (form.latitude && form.longitude) {
      fetchWeatherData(form.latitude, form.longitude, selectedCity?.id);
    }
  }, [form.latitude, form.longitude, selectedCity]);

  const handleCitySelect = (city) => {
    setSelectedCity(city);
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const payload = { ...form };
      Object.keys(payload).forEach(key => {
        if (key !== "roof_type") {
          if (payload[key] !== "" && payload[key] !== null && payload[key] !== undefined) {
            payload[key] = Number(payload[key]);
          } else {
            // Remove empty values so backend can use defaults
            delete payload[key];
          }
        }
      });
      
      const res = await axios.post("/api/predict", payload);
      setResult(res.data);
      
      // Pass location data to parent component
      if (onLocationSelect) {
        onLocationSelect({
          latitude: parseFloat(form.latitude),
          longitude: parseFloat(form.longitude),
          city: selectedCity
        });
      }
    } catch (error) {
      setError(error.response?.data?.message || "An error occurred while making the prediction");
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#2c3e50', marginBottom: '10px' }}>🌧️ TheGreenDrop</h1>
        <h2 style={{ color: '#34495e', fontWeight: '300' }}>Smart Rainwater Harvesting Prediction</h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
        {/* Form Section */}
        <div style={{ background: '#f8f9fa', padding: '25px', borderRadius: '10px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
          <h3 style={{ color: '#2c3e50', marginBottom: '20px' }}>📍 Location & Property Details</h3>
          
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gap: '15px' }}>
              {/* Location Section */}
              <div style={{ background: '#e8f4fd', padding: '15px', borderRadius: '8px', marginBottom: '10px' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#2980b9' }}>Location</h4>
                
                {/* City Selector */}
                <CitySelector onCitySelect={handleCitySelect} selectedCity={selectedCity} />
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '10px', alignItems: 'end' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
                      Latitude *
                    </label>
                    <input
                      name="latitude"
                      value={form.latitude}
                      onChange={handleChange}
                      type="number"
                      step="any"
                      required
                      style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
                      Longitude *
                    </label>
                    <input
                      name="longitude"
                      value={form.longitude}
                      onChange={handleChange}
                      type="number"
                      step="any"
                      required
                      style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                    />
                  </div>
                  <button
                    type="button"
                    onClick={getCurrentLocation}
                    style={{ padding: '8px 12px', background: '#3498db', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                  >
                    📍 Get Location
                  </button>
                </div>
              </div>

              {/* Weather Data Display */}
              {weatherData && (
                <div style={{ background: '#d5f4e6', padding: '15px', borderRadius: '8px', marginBottom: '10px' }}>
                  <h4 style={{ margin: '0 0 10px 0', color: '#27ae60' }}>🌤️ IMD Weather Data</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '14px' }}>
                    <div>Annual Rainfall: <strong>{weatherData.annual_rainfall_mm}mm</strong></div>
                    <div>Temperature: <strong>{weatherData.avg_temperature_c}°C</strong></div>
                    <div>Rainy Days: <strong>{weatherData.rainy_days_count}</strong></div>
                    <div>Evaporation: <strong>{weatherData.evaporation_rate_mmday}mm/day</strong></div>
                    {weatherData.infiltration_potential && (
                      <div>Infiltration: <strong>{(weatherData.infiltration_potential * 100).toFixed(1)}%</strong></div>
                    )}
                    {weatherData.recharge_efficiency && (
                      <div>Recharge Efficiency: <strong>{(weatherData.recharge_efficiency * 100).toFixed(1)}%</strong></div>
                    )}
                    {weatherData.data_source && (
                      <div style={{ gridColumn: '1 / -1', fontSize: '12px', color: '#666', marginTop: '5px' }}>
                        Data Source: {weatherData.data_source}
                      </div>
                    )}
                  </div>
                  
                  {/* Forecast Data */}
                  {weatherData.forecast_days && weatherData.forecast_days.length > 0 && (
                    <div style={{ marginTop: '10px', padding: '10px', background: 'rgba(255,255,255,0.7)', borderRadius: '6px' }}>
                      <h5 style={{ margin: '0 0 8px 0', fontSize: '13px', color: '#27ae60' }}>📅 7-Day Forecast</h5>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(80px, 1fr))', gap: '5px', fontSize: '11px' }}>
                        {weatherData.forecast_days.slice(0, 7).map((day, index) => (
                          <div key={index} style={{ textAlign: 'center', padding: '5px', background: 'white', borderRadius: '4px' }}>
                            <div style={{ fontWeight: 'bold' }}>{day.date || `Day ${index + 1}`}</div>
                            <div style={{ color: '#666' }}>{day.max_temp_c}°/{day.min_temp_c}°</div>
                            <div style={{ color: '#3498db' }}>{day.rainfall_mm}mm</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Monsoon Intensity */}
                  {weatherData.monsoon_intensity && (
                    <div style={{ marginTop: '10px', padding: '8px', background: 'rgba(255,255,255,0.7)', borderRadius: '6px' }}>
                      <div style={{ fontSize: '12px', color: '#27ae60' }}>
                        <strong>Monsoon Intensity:</strong> {weatherData.monsoon_intensity.monsoon_intensity || 'Moderate'}
                        {weatherData.monsoon_intensity.intensity_score && (
                          <span style={{ marginLeft: '10px' }}>
                            Score: {(weatherData.monsoon_intensity.intensity_score * 100).toFixed(0)}%
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Property Details */}
              <div style={{ background: '#fff3cd', padding: '15px', borderRadius: '8px', marginBottom: '10px' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#f39c12' }}>🏠 Property Details</h4>
                <div style={{ display: 'grid', gap: '10px' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
                      Roof Area (m²) *
                    </label>
                    <input
                      name="roof_area_m2"
                      value={form.roof_area_m2}
                      onChange={handleChange}
                      type="number"
                      step="any"
                      required
                      style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
                      Roof Type *
                    </label>
                    <select
                      name="roof_type"
                      value={form.roof_type}
                      onChange={handleChange}
                      required
                      style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                    >
                      {formFields.find(f => f.name === 'roof_type').options.map(opt => (
                        <option key={opt} value={opt}>{opt}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Advanced Options */}
              <details style={{ background: '#f8f9fa', padding: '15px', borderRadius: '8px' }}>
                <summary style={{ cursor: 'pointer', fontWeight: '500', marginBottom: '10px' }}>
                  🔧 Advanced Options (Optional)
                </summary>
                <div style={{ display: 'grid', gap: '10px' }}>
                  {formFields.filter(f => !f.required).map(field => (
                    <div key={field.name}>
                      <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>
                        {field.label}
                      </label>
                      <input
                        name={field.name}
                        value={form[field.name]}
                        onChange={handleChange}
                        type={field.type}
                        step={field.step}
                        placeholder={field.name === 'available_space_m2' ? 'Same as roof area' : ''}
                        style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                      />
                    </div>
                  ))}
                </div>
              </details>
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '12px',
                background: loading ? '#95a5a6' : '#27ae60',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '16px',
                fontWeight: '500',
                cursor: loading ? 'not-allowed' : 'pointer',
                marginTop: '20px'
              }}
            >
              {loading ? '🔄 Analyzing...' : '🚀 Get Prediction'}
            </button>
          </form>

          {error && (
            <div style={{ background: '#f8d7da', color: '#721c24', padding: '10px', borderRadius: '4px', marginTop: '10px' }}>
              ❌ {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        <div style={{ background: '#f8f9fa', padding: '25px', borderRadius: '10px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
          <h3 style={{ color: '#2c3e50', marginBottom: '20px' }}>📊 Prediction Results</h3>
          
          {result ? (
            <div>
              {/* Summary Card */}
              <div style={{ background: '#d4edda', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                <h4 style={{ margin: '0 0 15px 0', color: '#155724' }}>💡 Recommendation Summary</h4>
                <p style={{ margin: '0 0 10px 0', lineHeight: '1.6' }}>{result.summary}</p>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '15px' }}>
                  <div style={{ textAlign: 'center', padding: '10px', background: 'white', borderRadius: '6px' }}>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#27ae60' }}>
                      {result.recommended_tank_capacity_liters.toLocaleString()}L
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Tank Capacity</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '10px', background: 'white', borderRadius: '6px' }}>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#3498db' }}>
                      {result.feasibility_score.toFixed(1)}/10
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>Feasibility Score</div>
                  </div>
                </div>
              </div>

              {/* Detailed Results */}
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ color: '#2c3e50', marginBottom: '15px' }}>📈 Detailed Analysis</h4>
                <div style={{ display: 'grid', gap: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: 'white', borderRadius: '4px' }}>
                    <span>Feasibility Category:</span>
                    <strong style={{ color: '#27ae60' }}>{result.feasibility_category}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: 'white', borderRadius: '4px' }}>
                    <span>Recommended Structure:</span>
                    <strong style={{ color: '#3498db' }}>{result.recommended_structure}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: 'white', borderRadius: '4px' }}>
                    <span>Annual Rainfall:</span>
                    <strong>{result.weather_data.annual_rainfall_mm}mm</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px', background: 'white', borderRadius: '4px' }}>
                    <span>Runoff Coefficient:</span>
                    <strong>{result.roof_efficiency.runoff_coefficient}</strong>
                  </div>
                </div>
              </div>

              {/* Charts */}
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ color: '#2c3e50', marginBottom: '15px' }}>📊 Visualizations</h4>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={[
                    { name: "Feasibility Score", value: result.feasibility_score },
                    { name: "Max Score", value: 10 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 10]} />
                    <Tooltip />
                    <Bar dataKey="value" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Monthly Breakdown */}
              <div style={{ background: '#e3f2fd', padding: '15px', borderRadius: '8px' }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#1976d2' }}>📅 Monthly Water Harvest</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', fontSize: '12px' }}>
                  {Array.from({ length: 12 }, (_, i) => {
                    const month = new Date(2024, i).toLocaleString('default', { month: 'short' });
                    const monthly = Math.round(result.recommended_tank_capacity_liters / 12);
                    return (
                      <div key={i} style={{ textAlign: 'center', padding: '5px', background: 'white', borderRadius: '4px' }}>
                        <div style={{ fontWeight: 'bold' }}>{month}</div>
                        <div style={{ color: '#666' }}>{monthly}L</div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: '#7f8c8d', padding: '40px 20px' }}>
              <div style={{ fontSize: '48px', marginBottom: '20px' }}>🌧️</div>
              <p>Enter your location and property details to get personalized rainwater harvesting recommendations.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}