import React, { useState, useEffect } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from "recharts";

export default function Dashboard() {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch dashboard stats
      const statsResponse = await axios.get("/api/dashboard");
      setDashboardStats(statsResponse.data);
      
      // Fetch analytics
      const analyticsResponse = await axios.get("/api/analytics?days=30");
      setAnalytics(analyticsResponse.data);
      
      // Fetch trends
      const trendsResponse = await axios.get("/api/analytics/trends?metric_name=feasibility_score&days=30");
      setTrends(trendsResponse.data);
      
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setError("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <div style={{ fontSize: '24px', marginBottom: '20px' }}>📊</div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '40px', color: '#e74c3c' }}>
        <div style={{ fontSize: '24px', marginBottom: '20px' }}>❌</div>
        <p>{error}</p>
        <button 
          onClick={fetchDashboardData}
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
          Retry
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '20px' }}>
      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#2c3e50', marginBottom: '10px' }}>📊 GreenDrop Dashboard</h1>
        <h2 style={{ color: '#34495e', fontWeight: '300' }}>Analytics & Insights</h2>
      </div>

      {/* Stats Cards */}
      {dashboardStats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
          <div style={{ background: '#e8f4fd', padding: '20px', borderRadius: '10px', textAlign: 'center' }}>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#2980b9' }}>
              {dashboardStats.total_predictions}
            </div>
            <div style={{ color: '#666', fontSize: '14px' }}>Total Predictions</div>
          </div>
          
          <div style={{ background: '#d5f4e6', padding: '20px', borderRadius: '10px', textAlign: 'center' }}>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#27ae60' }}>
              {dashboardStats.today_predictions}
            </div>
            <div style={{ color: '#666', fontSize: '14px' }}>Today's Predictions</div>
          </div>
          
          <div style={{ background: '#fff3cd', padding: '20px', borderRadius: '10px', textAlign: 'center' }}>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#f39c12' }}>
              {dashboardStats.average_feasibility_score}/10
            </div>
            <div style={{ color: '#666', fontSize: '14px' }}>Avg Feasibility Score</div>
          </div>
          
          <div style={{ background: '#f8d7da', padding: '20px', borderRadius: '10px', textAlign: 'center' }}>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#e74c3c' }}>
              {Math.round(dashboardStats.average_tank_capacity)}L
            </div>
            <div style={{ color: '#666', fontSize: '14px' }}>Avg Tank Capacity</div>
          </div>
        </div>
      )}

      {/* Charts Section */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px', marginBottom: '30px' }}>
        {/* Feasibility Score Distribution */}
        <div style={{ background: '#f8f9fa', padding: '25px', borderRadius: '10px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
          <h3 style={{ color: '#2c3e50', marginBottom: '20px' }}>📈 Feasibility Score Trends</h3>
          {trends && trends.analytics && trends.analytics.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trends.analytics.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 10]} />
                <Tooltip />
                <Line type="monotone" dataKey="metric_value" stroke="#3498db" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#7f8c8d' }}>
              <div style={{ fontSize: '48px', marginBottom: '20px' }}>📊</div>
              <p>No trend data available</p>
            </div>
          )}
        </div>

        {/* Roof Type Distribution */}
        <div style={{ background: '#f8f9fa', padding: '25px', borderRadius: '10px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
          <h3 style={{ color: '#2c3e50', marginBottom: '20px' }}>🏠 Roof Type Distribution</h3>
          <div style={{ textAlign: 'center', padding: '40px', color: '#7f8c8d' }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>🏠</div>
            <p>Most Common: {dashboardStats?.most_common_roof_type || 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* Analytics Table */}
      {analytics && analytics.analytics && analytics.analytics.length > 0 && (
        <div style={{ background: '#f8f9fa', padding: '25px', borderRadius: '10px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
          <h3 style={{ color: '#2c3e50', marginBottom: '20px' }}>📋 Recent Analytics</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#e9ecef' }}>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Date</th>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Metric</th>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Value</th>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Location</th>
                </tr>
              </thead>
              <tbody>
                {analytics.analytics.slice(0, 10).map((item, index) => (
                  <tr key={index} style={{ borderBottom: '1px solid #dee2e6' }}>
                    <td style={{ padding: '12px' }}>{item.date}</td>
                    <td style={{ padding: '12px' }}>{item.metric_name}</td>
                    <td style={{ padding: '12px' }}>{item.metric_value}</td>
                    <td style={{ padding: '12px' }}>{item.location || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Trends Summary */}
      {trends && (
        <div style={{ background: '#e8f4fd', padding: '20px', borderRadius: '10px', marginTop: '20px' }}>
          <h3 style={{ color: '#2980b9', marginBottom: '15px' }}>📊 Trends Summary</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
            <div>
              <strong>Trend Direction:</strong> 
              <span style={{ 
                color: trends.trend === 'increasing' ? '#27ae60' : 
                       trends.trend === 'decreasing' ? '#e74c3c' : '#f39c12',
                marginLeft: '10px'
              }}>
                {trends.trend}
              </span>
            </div>
            <div>
              <strong>Change:</strong> 
              <span style={{ 
                color: trends.change_percent > 0 ? '#27ae60' : 
                       trends.change_percent < 0 ? '#e74c3c' : '#f39c12',
                marginLeft: '10px'
              }}>
                {trends.change_percent}%
              </span>
            </div>
            <div>
              <strong>Period:</strong> {trends.period_days} days
            </div>
            <div>
              <strong>Data Points:</strong> {trends.count}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
