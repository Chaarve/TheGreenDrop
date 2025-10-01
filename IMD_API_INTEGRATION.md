# IMD Weather API Integration for GreenDrop

## Overview

This document describes the comprehensive integration of India Meteorological Department (IMD) weather APIs into the GreenDrop rainwater harvesting prediction system. The integration provides real-time weather data, forecasts, and groundwater recharge metrics to enhance the accuracy of rainwater harvesting feasibility predictions.

## Integrated IMD APIs

### 1. City Weather Forecast (7 days)
- **URL**: `https://city.imd.gov.in/api/cityweather.php?id=42182`
- **Purpose**: Get 7-day weather forecast for specific cities
- **Parameters**: `id` (city ID)
- **Usage**: Provides temperature, rainfall, humidity forecasts

### 2. City Weather with Location
- **URL**: `https://city.imd.gov.in/api/cityweather_loc.php?id=42182`
- **Purpose**: Get weather data using latitude/longitude coordinates
- **Parameters**: `id` (city ID) or lat/lon coordinates
- **Usage**: More precise location-based weather data

### 3. Current Weather API
- **URL**: `https://mausam.imd.gov.in/api/current_wx_api.php?id=42182`
- **Purpose**: Get current weather conditions
- **Parameters**: `id` (city ID)
- **Usage**: Real-time temperature, humidity, pressure, wind data

### 4. District Wise Nowcast API
- **URL**: `https://mausam.imd.gov.in/api/nowcast_district_api.php?id=5`
- **Purpose**: Get district-wise weather nowcast
- **Parameters**: `id` (district ID)
- **Usage**: Short-term weather predictions for districts

### 5. District Wise Rainfall
- **URL**: `https://mausam.imd.gov.in/api/districtwise_rainfall_api.php`
- **Purpose**: Get rainfall data by district
- **Parameters**: None (returns all districts)
- **Usage**: Historical and current rainfall data

### 6. District Wise Warning
- **URL**: `https://mausam.imd.gov.in/api/warnings_district_api.php?id=1`
- **Purpose**: Get weather warnings and alerts
- **Parameters**: `id` (district ID)
- **Usage**: Weather alerts and warnings

### 7. Station Wise Nowcast API
- **URL**: `https://mausam.imd.gov.in/api/nowcastapi.php?id=Jaipur AP`
- **Purpose**: Get weather data from specific stations
- **Parameters**: `id` (station name)
- **Usage**: Station-specific weather data

### 8. State Wise Rainfall
- **URL**: `https://mausam.imd.gov.in/api/statewise_rainfall_api.php`
- **Purpose**: Get rainfall data by state
- **Parameters**: None
- **Usage**: State-level rainfall statistics

### 9. AWS/ARG Data
- **URL**: `https://city.imd.gov.in/api/aws_data_api.php`
- **Purpose**: Get Automatic Weather Station data
- **Parameters**: None
- **Usage**: Real-time weather station data

### 10. River Basin QPF
- **URL**: `https://mausam.imd.gov.in/api/basin_qpf_api.php`
- **Purpose**: Get Quantitative Precipitation Forecast for river basins
- **Parameters**: None
- **Usage**: Basin-level precipitation forecasts

### 11. Port Warning
- **URL**: `https://mausam.imd.gov.in/api/port_wx_api.php`
- **Purpose**: Get weather warnings for ports
- **Parameters**: None
- **Usage**: Maritime weather warnings

### 12. Sea Area Bulletin
- **URL**: `https://mausam.imd.gov.in/api/seaarea_bulletin_api.php`
- **Purpose**: Get sea area weather bulletins
- **Parameters**: None
- **Usage**: Marine weather information

### 13. Coastal Area Bulletin
- **URL**: `https://mausam.imd.gov.in/api/coastal_bulletin_api.php`
- **Purpose**: Get coastal area weather bulletins
- **Parameters**: None
- **Usage**: Coastal weather information

### 14. Subdivisional APIs
- **5-day Rainfall Forecast**: `https://mausam.imd.gov.in/api/api_5d_subdivisional_rf.php`
- **State-wise Districts RF Forecast**: `https://mausam.imd.gov.in/api/api_5d_statewisedistricts_rf_forecast.php`
- **Subdivision Wise Warning**: `https://mausam.imd.gov.in/api/api_subDivisionWiseWarning.php`
- **Subdivision Rainfall**: `https://mausam.imd.gov.in/api/subdivisionwise_rainfall_api.php`

## Implementation Details

### Weather Service Module (`weather_service.py`)

The `IMDWeatherService` class provides a comprehensive interface to all IMD APIs:

```python
from weather_service import IMDWeatherService

# Initialize service
weather_service = IMDWeatherService()

# Get comprehensive weather data
weather_data = weather_service.get_comprehensive_weather_data(
    latitude=28.6139, 
    longitude=77.2090, 
    city_id=42182
)
```

### Key Features

1. **Multi-Source Data Integration**: Combines data from multiple IMD APIs
2. **Fallback Mechanisms**: Graceful handling of API failures
3. **Recharge Metrics Calculation**: Specialized calculations for groundwater recharge
4. **Seasonal Analysis**: Monsoon intensity and seasonal patterns
5. **Error Handling**: Robust error handling with fallback data

### Calculated Metrics

The service calculates several groundwater recharge-specific metrics:

- **Evaporation Rate**: Calculated using temperature, humidity, and wind speed
- **Infiltration Potential**: Based on rainfall intensity and soil characteristics
- **Recharge Efficiency**: Combined metric considering multiple factors
- **Monsoon Intensity**: Classification of monsoon strength
- **Seasonal Factors**: Seasonal adjustments for recharge calculations

## API Endpoints

### 1. Get Comprehensive Weather Data
```
GET /weather?lat=28.6139&lon=77.2090&city_id=42182
```

**Response**:
```json
{
  "annual_rainfall_mm": 1200,
  "max_daily_rainfall_mm": 50,
  "rainy_days_count": 120,
  "avg_temperature_c": 25,
  "evaporation_rate_mmday": 4.5,
  "infiltration_potential": 0.6,
  "recharge_efficiency": 0.7,
  "monsoon_intensity": {
    "monsoon_intensity": "Moderate",
    "intensity_score": 0.5
  },
  "forecast_days": [...],
  "data_source": "IMD_API"
}
```

### 2. Get Weather Forecast
```
GET /weather/forecast?lat=28.6139&lon=77.2090
```

### 3. Get Weather Alerts
```
GET /weather/alerts?lat=28.6139&lon=77.2090
```

### 4. Get Recharge Metrics
```
GET /weather/recharge-metrics?lat=28.6139&lon=77.2090
```

### 5. Get Available Cities
```
GET /weather/cities
```

## City IDs

The system includes predefined city IDs for major Indian cities:

| City | ID | State |
|------|----|----|
| Delhi | 42182 | Delhi |
| Mumbai | 43003 | Maharashtra |
| Bangalore | 43295 | Karnataka |
| Chennai | 43279 | Tamil Nadu |
| Kolkata | 42809 | West Bengal |
| Hyderabad | 43128 | Telangana |
| Pune | 43047 | Maharashtra |
| Ahmedabad | 42647 | Gujarat |
| Jaipur | 42328 | Rajasthan |
| Lucknow | 42369 | Uttar Pradesh |

## Frontend Integration

The frontend has been enhanced to display:

1. **Real-time Weather Data**: Current weather conditions from IMD
2. **7-Day Forecast**: Visual forecast display
3. **Recharge Metrics**: Infiltration potential and recharge efficiency
4. **Monsoon Intensity**: Monsoon classification and intensity score
5. **Data Source**: Indication of data source (IMD_API or FALLBACK)

## Error Handling

The system implements multiple layers of error handling:

1. **API Timeout**: 10-second timeout for all API calls
2. **Fallback Data**: Default weather data when APIs fail
3. **Graceful Degradation**: System continues to function with limited data
4. **Logging**: Comprehensive logging of all API interactions

## Testing

A comprehensive test suite (`test_weather_integration.py`) is provided to verify:

1. All weather endpoints functionality
2. Multiple location testing
3. Prediction integration
4. Error handling scenarios
5. Performance testing

Run tests with:
```bash
python test_weather_integration.py
```

## Performance Considerations

1. **Caching**: Weather data is cached to reduce API calls
2. **Rate Limiting**: Built-in delays between API requests
3. **Parallel Processing**: Multiple API calls processed efficiently
4. **Timeout Management**: Prevents hanging requests

## Security Considerations

1. **No API Keys Required**: IMD APIs are publicly accessible
2. **Input Validation**: All inputs are validated before API calls
3. **Error Sanitization**: Error messages are sanitized before display
4. **Rate Limiting**: Prevents abuse of IMD APIs

## Future Enhancements

1. **Historical Data Integration**: Integration with historical weather APIs
2. **Machine Learning**: Weather pattern prediction using ML
3. **Real-time Updates**: WebSocket integration for real-time updates
4. **Mobile App**: Mobile-specific optimizations
5. **Analytics Dashboard**: Advanced weather analytics

## Troubleshooting

### Common Issues

1. **API Timeout**: Increase timeout values or check network connectivity
2. **Invalid City ID**: Verify city ID exists in the predefined list
3. **No Data Returned**: Check if IMD APIs are accessible
4. **Fallback Data**: System uses fallback data when APIs fail

### Debug Mode

Enable debug logging by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Support

For issues related to IMD API integration:

1. Check IMD API status: Visit IMD official website
2. Verify network connectivity
3. Check API response formats
4. Review error logs for specific issues

## Conclusion

The IMD weather API integration significantly enhances the GreenDrop system by providing:

- **Accurate Weather Data**: Real-time data from India's official meteorological department
- **Enhanced Predictions**: More accurate rainwater harvesting feasibility predictions
- **Comprehensive Coverage**: Multiple data sources for robust predictions
- **User Experience**: Rich weather information display in the frontend
- **Reliability**: Fallback mechanisms ensure system reliability

This integration makes GreenDrop a more comprehensive and accurate tool for rainwater harvesting planning in India.


