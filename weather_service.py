import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class IMDWeatherService:
    """
    Comprehensive weather service integrating multiple IMD (India Meteorological Department) APIs
    for enhanced groundwater recharge feasibility predictions.
    """
    
    def __init__(self):
        self.base_urls = {
            'city_weather': 'https://city.imd.gov.in/api/cityweather.php',
            'city_weather_loc': 'https://city.imd.gov.in/api/cityweather_loc.php',
            'current_weather': 'https://mausam.imd.gov.in/api/current_wx_api.php',
            'district_nowcast': 'https://mausam.imd.gov.in/api/nowcast_district_api.php',
            'district_rainfall': 'https://mausam.imd.gov.in/api/districtwise_rainfall_api.php',
            'district_warning': 'https://mausam.imd.gov.in/api/warnings_district_api.php',
            'station_nowcast': 'https://mausam.imd.gov.in/api/nowcastapi.php',
            'state_rainfall': 'https://mausam.imd.gov.in/api/statewise_rainfall_api.php',
            'aws_data': 'https://city.imd.gov.in/api/aws_data_api.php',
            'basin_qpf': 'https://mausam.imd.gov.in/api/basin_qpf_api.php',
            'port_warning': 'https://mausam.imd.gov.in/api/port_wx_api.php',
            'seaarea_bulletin': 'https://mausam.imd.gov.in/api/seaarea_bulletin_api.php',
            'coastal_bulletin': 'https://mausam.imd.gov.in/api/coastal_bulletin_api.php',
            'subdivisional_5d_rf': 'https://mausam.imd.gov.in/api/api_5d_subdivisional_rf.php',
            'statewise_districts_rf': 'https://mausam.imd.gov.in/api/api_5d_statewisedistricts_rf_forecast.php',
            'subdivision_warning': 'https://mausam.imd.gov.in/api/api_subDivisionWiseWarning.php',
            'subdivision_rainfall': 'https://mausam.imd.gov.in/api/subdivisionwise_rainfall_api.php'
        }
        
        # Common city IDs for major Indian cities
        self.city_ids = {
            'delhi': 42182,
            'mumbai': 43003,
            'bangalore': 43295,
            'chennai': 43279,
            'kolkata': 42809,
            'hyderabad': 43128,
            'pune': 43047,
            'ahmedabad': 42647,
            'jaipur': 42328,
            'lucknow': 42369
        }
        
        # Default weather data fallback
        self.default_weather = {
            'annual_rainfall_mm': 1200,
            'max_daily_rainfall_mm': 50,
            'rainy_days_count': 120,
            'avg_temperature_c': 25,
            'evaporation_rate_mmday': 4.5,
            'humidity_percent': 70,
            'wind_speed_kmh': 10,
            'pressure_hpa': 1013,
            'uv_index': 5
        }

    def get_comprehensive_weather_data(self, latitude: float, longitude: float, city_id: Optional[int] = None) -> Dict:
        """
        Get comprehensive weather data from multiple IMD sources
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            city_id: Optional city ID for IMD APIs
            
        Returns:
            Dictionary containing comprehensive weather data
        """
        try:
            # Get current weather data
            current_weather = self._get_current_weather_data(city_id)
            
            # Get 7-day forecast
            forecast_data = self._get_7day_forecast(city_id)
            
            # Get rainfall data
            rainfall_data = self._get_rainfall_data(latitude, longitude)
            
            # Get district-wise data
            district_data = self._get_district_data(latitude, longitude)
            
            # Combine all data sources
            comprehensive_data = self._combine_weather_data(
                current_weather, forecast_data, rainfall_data, district_data
            )
            
            # Calculate derived metrics for groundwater recharge
            comprehensive_data.update(self._calculate_recharge_metrics(comprehensive_data))
            
            logger.info(f"Successfully retrieved comprehensive weather data for lat: {latitude}, lon: {longitude}")
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"Error getting comprehensive weather data: {e}")
            return self._get_fallback_weather_data(latitude, longitude)

    def _get_current_weather_data(self, city_id: Optional[int] = None) -> Dict:
        """Get current weather data from IMD"""
        try:
            if city_id:
                url = f"{self.base_urls['current_weather']}?id={city_id}"
            else:
                url = self.base_urls['current_weather']
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_current_weather(data)
            
        except Exception as e:
            logger.warning(f"Failed to get current weather data: {e}")
            return {}

    def _get_7day_forecast(self, city_id: Optional[int] = None) -> Dict:
        """Get 7-day weather forecast from IMD"""
        try:
            if city_id:
                url = f"{self.base_urls['city_weather']}?id={city_id}"
            else:
                url = self.base_urls['city_weather']
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_forecast_data(data)
            
        except Exception as e:
            logger.warning(f"Failed to get forecast data: {e}")
            return {}

    def _get_rainfall_data(self, latitude: float, longitude: float) -> Dict:
        """Get rainfall data from multiple IMD sources"""
        try:
            rainfall_data = {}
            
            # Try district-wise rainfall
            try:
                response = requests.get(self.base_urls['district_rainfall'], timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    rainfall_data.update(self._parse_district_rainfall(data))
            except Exception as e:
                logger.warning(f"District rainfall API failed: {e}")
            
            # Try state-wise rainfall
            try:
                response = requests.get(self.base_urls['state_rainfall'], timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    rainfall_data.update(self._parse_state_rainfall(data))
            except Exception as e:
                logger.warning(f"State rainfall API failed: {e}")
            
            # Try subdivision rainfall
            try:
                response = requests.get(self.base_urls['subdivision_rainfall'], timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    rainfall_data.update(self._parse_subdivision_rainfall(data))
            except Exception as e:
                logger.warning(f"Subdivision rainfall API failed: {e}")
            
            return rainfall_data
            
        except Exception as e:
            logger.warning(f"Failed to get rainfall data: {e}")
            return {}

    def _get_district_data(self, latitude: float, longitude: float) -> Dict:
        """Get district-wise weather data"""
        try:
            district_data = {}
            
            # Try district nowcast
            try:
                response = requests.get(self.base_urls['district_nowcast'], timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    district_data.update(self._parse_district_nowcast(data))
            except Exception as e:
                logger.warning(f"District nowcast API failed: {e}")
            
            # Try district warnings
            try:
                response = requests.get(self.base_urls['district_warning'], timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    district_data.update(self._parse_district_warnings(data))
            except Exception as e:
                logger.warning(f"District warnings API failed: {e}")
            
            return district_data
            
        except Exception as e:
            logger.warning(f"Failed to get district data: {e}")
            return {}

    def _parse_current_weather(self, data: Dict) -> Dict:
        """Parse current weather data from IMD API response"""
        try:
            # This is a placeholder - actual parsing depends on IMD API response format
            # You may need to adjust based on the actual API response structure
            return {
                'current_temperature_c': data.get('temperature', 25),
                'current_humidity_percent': data.get('humidity', 70),
                'current_pressure_hpa': data.get('pressure', 1013),
                'current_wind_speed_kmh': data.get('wind_speed', 10),
                'current_weather_condition': data.get('condition', 'Clear'),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"Error parsing current weather: {e}")
            return {}

    def _parse_forecast_data(self, data: Dict) -> Dict:
        """Parse 7-day forecast data from IMD API response"""
        try:
            # This is a placeholder - actual parsing depends on IMD API response format
            forecast_days = []
            
            # Extract forecast data for each day
            if isinstance(data, list):
                for day_data in data[:7]:  # Limit to 7 days
                    forecast_days.append({
                        'date': day_data.get('date', ''),
                        'max_temp_c': day_data.get('max_temp', 30),
                        'min_temp_c': day_data.get('min_temp', 20),
                        'rainfall_mm': day_data.get('rainfall', 0),
                        'humidity_percent': day_data.get('humidity', 70),
                        'wind_speed_kmh': day_data.get('wind_speed', 10),
                        'weather_condition': day_data.get('condition', 'Clear')
                    })
            
            return {
                'forecast_days': forecast_days,
                'forecast_period_days': len(forecast_days)
            }
        except Exception as e:
            logger.warning(f"Error parsing forecast data: {e}")
            return {}

    def _parse_district_rainfall(self, data: Dict) -> Dict:
        """Parse district-wise rainfall data"""
        try:
            # Calculate average rainfall from district data
            total_rainfall = 0
            count = 0
            
            if isinstance(data, list):
                for district in data:
                    if 'rainfall' in district:
                        total_rainfall += float(district['rainfall'])
                        count += 1
            
            avg_rainfall = total_rainfall / count if count > 0 else 1200
            
            return {
                'district_avg_rainfall_mm': avg_rainfall,
                'district_rainfall_data_points': count
            }
        except Exception as e:
            logger.warning(f"Error parsing district rainfall: {e}")
            return {}

    def _parse_state_rainfall(self, data: Dict) -> Dict:
        """Parse state-wise rainfall data"""
        try:
            # Similar parsing logic for state data
            return {
                'state_rainfall_mm': data.get('rainfall', 1200),
                'state_name': data.get('state', 'Unknown')
            }
        except Exception as e:
            logger.warning(f"Error parsing state rainfall: {e}")
            return {}

    def _parse_subdivision_rainfall(self, data: Dict) -> Dict:
        """Parse subdivision-wise rainfall data"""
        try:
            return {
                'subdivision_rainfall_mm': data.get('rainfall', 1200),
                'subdivision_name': data.get('subdivision', 'Unknown')
            }
        except Exception as e:
            logger.warning(f"Error parsing subdivision rainfall: {e}")
            return {}

    def _parse_district_nowcast(self, data: Dict) -> Dict:
        """Parse district nowcast data"""
        try:
            return {
                'nowcast_condition': data.get('condition', 'Normal'),
                'nowcast_warning': data.get('warning', 'None'),
                'nowcast_timestamp': data.get('timestamp', datetime.now().isoformat())
            }
        except Exception as e:
            logger.warning(f"Error parsing district nowcast: {e}")
            return {}

    def _parse_district_warnings(self, data: Dict) -> Dict:
        """Parse district warning data"""
        try:
            return {
                'active_warnings': data.get('warnings', []),
                'warning_level': data.get('level', 'Normal'),
                'warning_type': data.get('type', 'None')
            }
        except Exception as e:
            logger.warning(f"Error parsing district warnings: {e}")
            return {}

    def _combine_weather_data(self, current: Dict, forecast: Dict, rainfall: Dict, district: Dict) -> Dict:
        """Combine data from all sources into comprehensive weather data"""
        combined = {}
        
        # Start with default values
        combined.update(self.default_weather)
        
        # Add current weather data
        combined.update(current)
        
        # Add forecast data
        combined.update(forecast)
        
        # Add rainfall data
        combined.update(rainfall)
        
        # Add district data
        combined.update(district)
        
        # Calculate derived metrics
        combined.update(self._calculate_derived_metrics(combined))
        
        return combined

    def _calculate_derived_metrics(self, data: Dict) -> Dict:
        """Calculate derived weather metrics"""
        try:
            # Calculate average temperature from forecast if available
            if 'forecast_days' in data and data['forecast_days']:
                temps = [day.get('max_temp_c', 25) + day.get('min_temp_c', 20) for day in data['forecast_days']]
                avg_temp = sum(temps) / (2 * len(temps)) if temps else 25
            else:
                avg_temp = data.get('current_temperature_c', 25)
            
            # Calculate total forecast rainfall
            forecast_rainfall = 0
            if 'forecast_days' in data and data['forecast_days']:
                forecast_rainfall = sum(day.get('rainfall_mm', 0) for day in data['forecast_days'])
            
            # Estimate rainy days from forecast
            rainy_days = 0
            if 'forecast_days' in data and data['forecast_days']:
                rainy_days = sum(1 for day in data['forecast_days'] if day.get('rainfall_mm', 0) > 0)
            
            return {
                'avg_temperature_c': avg_temp,
                'forecast_total_rainfall_mm': forecast_rainfall,
                'forecast_rainy_days': rainy_days,
                'data_source': 'IMD_API',
                'data_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"Error calculating derived metrics: {e}")
            return {}

    def _calculate_recharge_metrics(self, data: Dict) -> Dict:
        """Calculate groundwater recharge specific metrics"""
        try:
            # Calculate evaporation rate using Penman-Monteith approximation
            temp = data.get('avg_temperature_c', 25)
            humidity = data.get('current_humidity_percent', 70)
            wind_speed = data.get('current_wind_speed_kmh', 10)
            
            # Simplified evaporation calculation
            evaporation_rate = max(0.1, (temp - 10) * (100 - humidity) / 1000 * (1 + wind_speed / 50))
            
            # Calculate infiltration potential
            annual_rainfall = data.get('annual_rainfall_mm', 1200)
            infiltration_potential = min(1.0, annual_rainfall / 2000)  # Normalize to 2000mm max
            
            # Calculate recharge efficiency
            recharge_efficiency = infiltration_potential * (1 - evaporation_rate / 10)
            
            return {
                'evaporation_rate_mmday': round(evaporation_rate, 2),
                'infiltration_potential': round(infiltration_potential, 3),
                'recharge_efficiency': round(recharge_efficiency, 3),
                'recharge_seasonality': self._calculate_seasonality(data),
                'monsoon_intensity': self._calculate_monsoon_intensity(data)
            }
        except Exception as e:
            logger.warning(f"Error calculating recharge metrics: {e}")
            return {}

    def _calculate_seasonality(self, data: Dict) -> Dict:
        """Calculate seasonal patterns for recharge"""
        try:
            # Estimate seasonal patterns based on current data
            current_month = datetime.now().month
            
            # Indian monsoon seasons
            monsoon_months = [6, 7, 8, 9]  # June to September
            pre_monsoon = [3, 4, 5]  # March to May
            post_monsoon = [10, 11]  # October to November
            winter = [12, 1, 2]  # December to February
            
            if current_month in monsoon_months:
                season = 'Monsoon'
                recharge_factor = 1.5
            elif current_month in pre_monsoon:
                season = 'Pre-Monsoon'
                recharge_factor = 0.8
            elif current_month in post_monsoon:
                season = 'Post-Monsoon'
                recharge_factor = 1.2
            else:
                season = 'Winter'
                recharge_factor = 0.5
            
            return {
                'current_season': season,
                'recharge_factor': recharge_factor,
                'seasonal_rainfall_adjustment': recharge_factor
            }
        except Exception as e:
            logger.warning(f"Error calculating seasonality: {e}")
            return {'current_season': 'Unknown', 'recharge_factor': 1.0}

    def _calculate_monsoon_intensity(self, data: Dict) -> Dict:
        """Calculate monsoon intensity metrics"""
        try:
            annual_rainfall = data.get('annual_rainfall_mm', 1200)
            max_daily = data.get('max_daily_rainfall_mm', 50)
            
            # Classify monsoon intensity
            if annual_rainfall > 2000:
                intensity = 'Very High'
                intensity_score = 0.9
            elif annual_rainfall > 1500:
                intensity = 'High'
                intensity_score = 0.7
            elif annual_rainfall > 1000:
                intensity = 'Moderate'
                intensity_score = 0.5
            elif annual_rainfall > 500:
                intensity = 'Low'
                intensity_score = 0.3
            else:
                intensity = 'Very Low'
                intensity_score = 0.1
            
            return {
                'monsoon_intensity': intensity,
                'intensity_score': intensity_score,
                'peak_rainfall_capacity': max_daily,
                'annual_rainfall_classification': intensity
            }
        except Exception as e:
            logger.warning(f"Error calculating monsoon intensity: {e}")
            return {'monsoon_intensity': 'Unknown', 'intensity_score': 0.5}

    def _get_fallback_weather_data(self, latitude: float, longitude: float) -> Dict:
        """Get fallback weather data when APIs fail"""
        logger.warning(f"Using fallback weather data for lat: {latitude}, lon: {longitude}")
        
        fallback_data = self.default_weather.copy()
        
        # Add location-specific adjustments
        fallback_data.update({
            'latitude': latitude,
            'longitude': longitude,
            'data_source': 'FALLBACK',
            'data_timestamp': datetime.now().isoformat(),
            'api_status': 'Failed - Using fallback data'
        })
        
        # Calculate recharge metrics for fallback data
        fallback_data.update(self._calculate_recharge_metrics(fallback_data))
        
        return fallback_data

    def get_weather_alerts(self, latitude: float, longitude: float) -> List[Dict]:
        """Get weather alerts and warnings for the location"""
        try:
            alerts = []
            
            # Try to get district warnings
            try:
                response = requests.get(self.base_urls['district_warning'], timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    alerts.extend(self._parse_alerts(data))
            except Exception as e:
                logger.warning(f"Failed to get weather alerts: {e}")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting weather alerts: {e}")
            return []

    def _parse_alerts(self, data: Dict) -> List[Dict]:
        """Parse weather alerts from API response"""
        try:
            alerts = []
            if isinstance(data, list):
                for alert in data:
                    alerts.append({
                        'type': alert.get('type', 'Unknown'),
                        'level': alert.get('level', 'Normal'),
                        'message': alert.get('message', ''),
                        'timestamp': alert.get('timestamp', datetime.now().isoformat())
                    })
            return alerts
        except Exception as e:
            logger.warning(f"Error parsing alerts: {e}")
            return []

    def get_historical_weather_trends(self, latitude: float, longitude: float, days: int = 30) -> Dict:
        """Get historical weather trends (placeholder for future implementation)"""
        try:
            # This would typically integrate with historical weather APIs
            # For now, return estimated trends based on location
            return {
                'trend_period_days': days,
                'avg_temperature_trend': 'stable',
                'rainfall_trend': 'normal',
                'humidity_trend': 'stable',
                'data_availability': 'limited'
            }
        except Exception as e:
            logger.warning(f"Error getting historical trends: {e}")
            return {}

    def _get_station_data(self, latitude: float, longitude: float, station_name: Optional[str] = None) -> Dict:
        """Get weather station data for a location"""
        try:
            station_data = {}
            
            # Try station nowcast if station name provided
            if station_name:
                try:
                    url = f"{self.base_urls['station_nowcast']}?id={station_name}"
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        station_data.update(self._parse_station_nowcast(data))
                except Exception as e:
                    logger.warning(f"Station nowcast API failed: {e}")
            
            # Try AWS data
            try:
                response = requests.get(self.base_urls['aws_data'], timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    station_data.update(self._parse_aws_data(data))
            except Exception as e:
                logger.warning(f"AWS data API failed: {e}")
            
            return station_data
            
        except Exception as e:
            logger.warning(f"Error getting station data: {e}")
            return {}

    def _parse_station_nowcast(self, data: Dict) -> Dict:
        """Parse station nowcast data"""
        try:
            return {
                'station_condition': data.get('condition', 'Normal'),
                'station_temperature': data.get('temperature', 25),
                'station_humidity': data.get('humidity', 70),
                'station_pressure': data.get('pressure', 1013),
                'station_wind_speed': data.get('wind_speed', 10),
                'station_timestamp': data.get('timestamp', datetime.now().isoformat())
            }
        except Exception as e:
            logger.warning(f"Error parsing station nowcast: {e}")
            return {}

    def _parse_aws_data(self, data: Dict) -> Dict:
        """Parse AWS (Automatic Weather Station) data"""
        try:
            return {
                'aws_temperature': data.get('temperature', 25),
                'aws_humidity': data.get('humidity', 70),
                'aws_pressure': data.get('pressure', 1013),
                'aws_wind_speed': data.get('wind_speed', 10),
                'aws_wind_direction': data.get('wind_direction', 'N'),
                'aws_rainfall': data.get('rainfall', 0),
                'aws_timestamp': data.get('timestamp', datetime.now().isoformat())
            }
        except Exception as e:
            logger.warning(f"Error parsing AWS data: {e}")
            return {}

# Utility functions for external use
def get_weather_for_location(latitude: float, longitude: float, city_id: Optional[int] = None) -> Dict:
    """
    Convenience function to get weather data for a location
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        city_id: Optional city ID for IMD APIs
        
    Returns:
        Dictionary containing comprehensive weather data
    """
    service = IMDWeatherService()
    return service.get_comprehensive_weather_data(latitude, longitude, city_id)

def get_weather_alerts_for_location(latitude: float, longitude: float) -> List[Dict]:
    """
    Convenience function to get weather alerts for a location
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        List of weather alerts
    """
    service = IMDWeatherService()
    return service.get_weather_alerts(latitude, longitude)


