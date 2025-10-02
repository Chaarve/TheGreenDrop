from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import requests
import os
from datetime import datetime, timedelta
import logging
from database import DatabaseManager
from weather_service import IMDWeatherService, get_weather_for_location, get_weather_alerts_for_location

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load your models and preprocessing objects
clf = joblib.load("feasibility_category_model.joblib")
reg = joblib.load("feasibility_score_model.joblib")
reco = joblib.load("recommended_structure_model.joblib")
scaler = joblib.load("scaler.joblib")
model_features = joblib.load("model_features.joblib")

# Weather API Configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'your_openweather_api_key_here')
IMD_API_BASE = "https://mausam.imd.gov.in/data/"

# Initialize IMD Weather Service
imd_weather_service = IMDWeatherService()

# Initialize weather service and database
weather_service = imd_weather_service
db_manager = DatabaseManager()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        logger.info(f"Received prediction request: {data}")
        
        # 1. Get location, roof_type, roof_area from data
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        roof_type = data.get('roof_type')
        roof_area = data.get('roof_area_m2')
        available_space = data.get('available_space_m2', roof_area)

        # 2. Get real weather data using IMD APIs
        weather_data = weather_service.get_comprehensive_weather_data(latitude, longitude)
        logger.info(f"Weather data retrieved: {weather_data}")

        # 3. Prepare comprehensive features for ML model
        features = {
            'annual_rainfall_mm': weather_data['annual_rainfall_mm'],
            'max_daily_rainfall_mm': weather_data['max_daily_rainfall_mm'],
            'rainy_days_count': weather_data['rainy_days_count'],
            'avg_temperature_c': weather_data['avg_temperature_c'],
            'evaporation_rate_mmday': weather_data['evaporation_rate_mmday'],
            'clay_pct': data.get('clay_pct', 30),  # Default soil composition
            'sand_pct': data.get('sand_pct', 40),
            'silt_pct': data.get('silt_pct', 30),
            'latitude': latitude,
            'longitude': longitude,
            'elevation_m': data.get('elevation_m', 100),  # Default elevation
            'roof_area_m2': roof_area,
            'available_space_m2': available_space,
            'roof_type': roof_type,
            'infiltration_rate_mmhr': data.get('infiltration_rate_mmhr', 10),
            'runoff_coefficient': float(data.get('runoff_coefficient', 0.8)),
            'annual_runoff_m3': data.get('annual_runoff_m3', 0)
        }

        # Ensure all numeric features are actually numeric (convert strings to float)
        numeric_features = ['annual_rainfall_mm', 'max_daily_rainfall_mm', 'rainy_days_count', 
                           'avg_temperature_c', 'evaporation_rate_mmday', 'clay_pct', 'sand_pct', 
                           'silt_pct', 'latitude', 'longitude', 'elevation_m', 'roof_area_m2', 
                           'available_space_m2', 'infiltration_rate_mmhr', 'runoff_coefficient', 
                           'annual_runoff_m3']
        
        for feature in numeric_features:
            if feature in features:
                try:
                    features[feature] = float(features[feature])
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {feature} to float, using default value")
                    features[feature] = 0.0

        # Calculate derived features
        features['rainfall_intensity'] = features['max_daily_rainfall_mm'] / (features['rainy_days_count'] + 1)
        features['soil_water_capacity'] = features['clay_pct'] * 0.4 + features['silt_pct'] * 0.3 + features['sand_pct'] * 0.1
        features['roof_efficiency'] = features['roof_area_m2'] / (features['available_space_m2'] + 1)
        features['climate_aridity'] = features['evaporation_rate_mmday'] / ((features['annual_rainfall_mm'] / 365) + 0.1)
        features['harvest_potential'] = features['annual_rainfall_mm'] * features['roof_area_m2'] * features['runoff_coefficient'] / 1000
        features['temperature_factor'] = features['avg_temperature_c'] / 30
        features['elevation_factor'] = features['elevation_m'] / 1000

        # Calculate annual runoff if not provided
        if features['annual_runoff_m3'] == 0:
            annual_rainfall_m = features['annual_rainfall_mm'] / 1000
            features['annual_runoff_m3'] = roof_area * annual_rainfall_m * features['runoff_coefficient']
            
        # Calculate annual harvestable water in liters
        annual_rainfall_m = features['annual_rainfall_mm'] / 1000
        annual_harvestable = roof_area * annual_rainfall_m * features['runoff_coefficient'] * 1000  # liters per year

        # 4. Prepare data for ML model prediction
        df_features = pd.DataFrame([features])
        
        # One-hot encode roof_type
        df_encoded = pd.get_dummies(df_features, columns=['roof_type'])
        
        # Ensure all required columns are present
        required_columns = model_features
        for col in required_columns:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        
        # Reorder columns to match training data
        df_encoded = df_encoded[required_columns]
        
        # Scale features
        X_scaled = scaler.transform(df_encoded)
        
        # 5. Make ML predictions
        feasibility_category = clf.predict(X_scaled)[0]
        feasibility_score = reg.predict(X_scaled)[0]
        recommended_structure = reco.predict(X_scaled)[0]
        
        # 6. Calculate practical recommendations
        annual_rainfall_m = features['annual_rainfall_mm'] / 1000
        annual_harvestable = roof_area * annual_rainfall_m * features['runoff_coefficient'] * 1000  # liters per year
        
        # Assuming 200L per person per day for 4 people = 800L/day
        daily_usage = 800  # liters per day
        
        # Calculate monthly distribution based on typical Indian rainfall patterns
        # These percentages represent typical monthly rainfall distribution in India
        monthly_rainfall_distribution = {
            'January': 0.01,  # 1% of annual rainfall
            'February': 0.01,
            'March': 0.02,
            'April': 0.03,
            'May': 0.05,
            'June': 0.15,    # Monsoon starts
            'July': 0.25,    # Peak monsoon
            'August': 0.20,
            'September': 0.15,
            'October': 0.08,
            'November': 0.03,
            'December': 0.02
        }
        
        # Calculate monthly harvestable water
        monthly_harvestable = {}
        monthly_storage_requirements = {}
        
        # Define days in each month for more accurate calculations
        days_in_month = {
            'January': 31, 'February': 28, 'March': 31, 'April': 30, 
            'May': 31, 'June': 30, 'July': 31, 'August': 31, 
            'September': 30, 'October': 31, 'November': 30, 'December': 31
        }
        
        for month, percentage in monthly_rainfall_distribution.items():
            # Calculate harvestable water for this month
            month_harvestable = annual_harvestable * percentage
            monthly_harvestable[month] = int(month_harvestable)
            
            # Calculate required storage for this month
            # Storage needed = monthly usage - harvestable water (if usage > harvest)
            monthly_usage = daily_usage * days_in_month[month]
            
            # If monthly harvest exceeds usage, we need less storage
            # If monthly harvest is less than usage, we need more storage to compensate
            storage_requirement = max(monthly_usage - month_harvestable, 0)
            # Add buffer for dry spells (20%)
            monthly_storage_requirements[month] = int(storage_requirement * 1.2)
        
        # Traditional tank capacity calculation (for backward compatibility)
        monsoon_days = 90  # 3 months of monsoon season
        tank_capacity = min(annual_harvestable * 0.3, daily_usage * monsoon_days)  # Max 30% of annual or 3 months storage
        
        # 7. Generate comprehensive response
        response = {
            "feasibility_category": feasibility_category,
            "feasibility_score": float(feasibility_score),
            "recommended_structure": recommended_structure,
            "recommended_tank_capacity_liters": int(tank_capacity),
            "monthly_storage_requirements": monthly_storage_requirements,
            "monthly_harvestable": monthly_harvestable,
            "weather_data": weather_data,
            "roof_efficiency": {
                "runoff_coefficient": features['runoff_coefficient'],
                "annual_rainfall_mm": features['annual_rainfall_mm'],
                "annual_harvestable_liters": int(annual_harvestable),
                "recommended_tank_liters": int(tank_capacity)
            },
            "recommendations": {
                "tank_size": f"{int(tank_capacity)} liters",
                "roof_utilization": f"{roof_area} m²",
                "annual_harvest": f"{int(annual_harvestable)} liters/year",
                "monthly_average": f"{int(annual_harvestable/12)} liters/month"
            },
            "summary": (
                f"For your location (lat: {latitude}, lon: {longitude}) with a {roof_type} roof of {roof_area} m², "
                f"you can harvest approximately {int(annual_harvestable):,} liters annually from {features['annual_rainfall_mm']}mm rainfall. "
                f"We recommend a storage tank of {int(tank_capacity):,} liters for practical daily use. "
                f"Feasibility: {feasibility_category} (Score: {feasibility_score:.2f})"
            )
        }
        
        # 8. Save prediction to database
        try:
            prediction_data = {
                'user_id': data.get('user_id'),
                'latitude': latitude,
                'longitude': longitude,
                'roof_area_m2': roof_area,
                'roof_type': roof_type,
                'feasibility_category': feasibility_category,
                'feasibility_score': float(feasibility_score),
                'recommended_structure': recommended_structure,
                'recommended_tank_capacity_liters': int(tank_capacity),
                'weather_data': weather_data
            }
            prediction_id = db_manager.save_prediction(prediction_data)
            response['prediction_id'] = prediction_id
            
            # Save weather data
            db_manager.save_weather_data(weather_data, latitude, longitude)
            
            # Save analytics
            db_manager.save_analytics('feasibility_score', float(feasibility_score), f"{latitude},{longitude}")
            db_manager.save_analytics('tank_capacity', int(tank_capacity), f"{latitude},{longitude}")
            
        except Exception as e:
            logger.warning(f"Failed to save to database: {e}")
        
        logger.info(f"Prediction completed successfully")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            "error": "Prediction failed",
            "message": str(e)
        }), 500

@app.route('/weather', methods=['GET'])
def get_weather():
    """Get comprehensive weather data for a location using IMD APIs"""
    try:
        latitude = request.args.get('lat', type=float)
        longitude = request.args.get('lon', type=float)
        city_id = request.args.get('city_id', type=int)
        
        if not latitude or not longitude:
            return jsonify({"error": "Latitude and longitude are required"}), 400
        
        weather_data = weather_service.get_comprehensive_weather_data(latitude, longitude, city_id)
        return jsonify(weather_data)
        
    except Exception as e:
        logger.error(f"Weather data error: {str(e)}")
        return jsonify({"error": "Failed to fetch weather data"}), 500

@app.route('/weather/forecast', methods=['GET'])
def get_weather_forecast():
    """Get 7-day weather forecast for a location"""
    try:
        latitude = request.args.get('lat', type=float)
        longitude = request.args.get('lon', type=float)
        city_id = request.args.get('city_id', type=int)
        
        if not latitude or not longitude:
            return jsonify({"error": "Latitude and longitude are required"}), 400
        
        weather_data = weather_service.get_comprehensive_weather_data(latitude, longitude, city_id)
        forecast_data = {
            'forecast_days': weather_data.get('forecast_days', []),
            'forecast_period_days': weather_data.get('forecast_period_days', 0),
            'forecast_total_rainfall_mm': weather_data.get('forecast_total_rainfall_mm', 0),
            'forecast_rainy_days': weather_data.get('forecast_rainy_days', 0)
        }
        
        return jsonify(forecast_data)
        
    except Exception as e:
        logger.error(f"Weather forecast error: {str(e)}")
        return jsonify({"error": "Failed to fetch weather forecast"}), 500

@app.route('/weather/alerts', methods=['GET'])
def get_weather_alerts():
    """Get weather alerts and warnings for a location"""
    try:
        latitude = request.args.get('lat', type=float)
        longitude = request.args.get('lon', type=float)
        
        if not latitude or not longitude:
            return jsonify({"error": "Latitude and longitude are required"}), 400
        
        alerts = weather_service.get_weather_alerts(latitude, longitude)
        return jsonify({
            "alerts": alerts,
            "count": len(alerts),
            "location": {"latitude": latitude, "longitude": longitude}
        })
        
    except Exception as e:
        logger.error(f"Weather alerts error: {str(e)}")
        return jsonify({"error": "Failed to fetch weather alerts"}), 500

@app.route('/weather/recharge-metrics', methods=['GET'])
def get_recharge_metrics():
    """Get groundwater recharge specific metrics for a location"""
    try:
        latitude = request.args.get('lat', type=float)
        longitude = request.args.get('lon', type=float)
        
        if not latitude or not longitude:
            return jsonify({"error": "Latitude and longitude are required"}), 400
        
        weather_data = weather_service.get_comprehensive_weather_data(latitude, longitude)
        
        recharge_metrics = {
            'evaporation_rate_mmday': weather_data.get('evaporation_rate_mmday', 4.5),
            'infiltration_potential': weather_data.get('infiltration_potential', 0.6),
            'recharge_efficiency': weather_data.get('recharge_efficiency', 0.7),
            'recharge_seasonality': weather_data.get('recharge_seasonality', {}),
            'monsoon_intensity': weather_data.get('monsoon_intensity', {}),
            'annual_rainfall_mm': weather_data.get('annual_rainfall_mm', 1200),
            'rainy_days_count': weather_data.get('rainy_days_count', 120),
            'data_source': weather_data.get('data_source', 'IMD_API')
        }
        
        return jsonify(recharge_metrics)
        
    except Exception as e:
        logger.error(f"Recharge metrics error: {str(e)}")
        return jsonify({"error": "Failed to fetch recharge metrics"}), 500

@app.route('/weather/cities', methods=['GET'])
def get_city_list():
    """Get list of available cities with their IDs"""
    try:
        cities = [
            {"name": "Delhi", "id": 42182, "state": "Delhi"},
            {"name": "Mumbai", "id": 43003, "state": "Maharashtra"},
            {"name": "Bangalore", "id": 43295, "state": "Karnataka"},
            {"name": "Chennai", "id": 43279, "state": "Tamil Nadu"},
            {"name": "Kolkata", "id": 42809, "state": "West Bengal"},
            {"name": "Hyderabad", "id": 43128, "state": "Telangana"},
            {"name": "Pune", "id": 43047, "state": "Maharashtra"},
            {"name": "Ahmedabad", "id": 42647, "state": "Gujarat"},
            {"name": "Jaipur", "id": 42328, "state": "Rajasthan"},
            {"name": "Lucknow", "id": 42369, "state": "Uttar Pradesh"}
        ]
        
        return jsonify({
            "cities": cities,
            "count": len(cities),
            "note": "Use city_id parameter in weather endpoints for city-specific data"
        })
        
    except Exception as e:
        logger.error(f"City list error: {str(e)}")
        return jsonify({"error": "Failed to fetch city list"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": {
            "classifier": clf is not None,
            "regressor": reg is not None,
            "recommender": reco is not None,
            "scaler": scaler is not None
        }
    })

@app.route('/predictions', methods=['GET'])
def get_predictions():
    """Get predictions from database"""
    try:
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 100))
        
        predictions = db_manager.get_predictions(user_id, limit)
        return jsonify({
            "predictions": predictions,
            "count": len(predictions)
        })
    except Exception as e:
        logger.error(f"Error retrieving predictions: {str(e)}")
        return jsonify({"error": "Failed to retrieve predictions"}), 500

@app.route('/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = db_manager.get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error retrieving dashboard stats: {str(e)}")
        return jsonify({"error": "Failed to retrieve dashboard statistics"}), 500

@app.route('/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    try:
        metric_name = request.args.get('metric_name')
        days = int(request.args.get('days', 30))
        
        analytics = db_manager.get_analytics(metric_name, days)
        return jsonify({
            "analytics": analytics,
            "count": len(analytics)
        })
    except Exception as e:
        logger.error(f"Error retrieving analytics: {str(e)}")
        return jsonify({"error": "Failed to retrieve analytics"}), 500

@app.route('/export/<table_name>', methods=['GET'])
def export_data(table_name):
    """Export data from a specific table"""
    try:
        allowed_tables = ['predictions', 'weather_data', 'analytics', 'users']
        if table_name not in allowed_tables:
            return jsonify({"error": "Invalid table name"}), 400
        
        df = db_manager.export_data(table_name)
        return jsonify({
            "table": table_name,
            "data": df.to_dict('records'),
            "count": len(df)
        })
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({"error": "Failed to export data"}), 500

@app.route('/weather/historical', methods=['GET'])
def get_historical_weather():
    """Get historical weather trends for a location"""
    try:
        latitude = request.args.get('lat', type=float)
        longitude = request.args.get('lon', type=float)
        days = int(request.args.get('days', 30))
        
        if not latitude or not longitude:
            return jsonify({"error": "Latitude and longitude are required"}), 400
        
        # Get historical data from database
        historical_data = db_manager.get_weather_data(latitude, longitude, days)
        
        return jsonify({
            "historical_data": historical_data,
            "period_days": days,
            "location": {"latitude": latitude, "longitude": longitude}
        })
        
    except Exception as e:
        logger.error(f"Historical weather error: {str(e)}")
        return jsonify({"error": "Failed to fetch historical weather data"}), 500

@app.route('/weather/station-data', methods=['GET'])
def get_station_data():
    """Get weather station data for a location"""
    try:
        latitude = request.args.get('lat', type=float)
        longitude = request.args.get('lon', type=float)
        station_name = request.args.get('station')
        
        if not latitude or not longitude:
            return jsonify({"error": "Latitude and longitude are required"}), 400
        
        # Get station data from IMD
        station_data = weather_service._get_station_data(latitude, longitude, station_name)
        
        return jsonify(station_data)
        
    except Exception as e:
        logger.error(f"Station data error: {str(e)}")
        return jsonify({"error": "Failed to fetch station data"}), 500

@app.route('/weather/monsoon-analysis', methods=['GET'])
def get_monsoon_analysis():
    """Get detailed monsoon analysis for a location"""
    try:
        latitude = request.args.get('lat', type=float)
        longitude = request.args.get('lon', type=float)
        
        if not latitude or not longitude:
            return jsonify({"error": "Latitude and longitude are required"}), 400
        
        weather_data = weather_service.get_comprehensive_weather_data(latitude, longitude)
        
        monsoon_analysis = {
            'monsoon_intensity': weather_data.get('monsoon_intensity', {}),
            'seasonal_patterns': weather_data.get('recharge_seasonality', {}),
            'rainfall_distribution': {
                'annual_rainfall_mm': weather_data.get('annual_rainfall_mm', 0),
                'max_daily_rainfall_mm': weather_data.get('max_daily_rainfall_mm', 0),
                'rainy_days_count': weather_data.get('rainy_days_count', 0)
            },
            'recharge_potential': {
                'infiltration_potential': weather_data.get('infiltration_potential', 0),
                'recharge_efficiency': weather_data.get('recharge_efficiency', 0),
                'evaporation_rate_mmday': weather_data.get('evaporation_rate_mmday', 0)
            }
        }
        
        return jsonify(monsoon_analysis)
        
    except Exception as e:
        logger.error(f"Monsoon analysis error: {str(e)}")
        return jsonify({"error": "Failed to fetch monsoon analysis"}), 500

@app.route('/predictions/user/<user_id>', methods=['GET'])
def get_user_predictions(user_id):
    """Get predictions for a specific user"""
    try:
        limit = int(request.args.get('limit', 50))
        predictions = db_manager.get_predictions(user_id, limit)
        
        return jsonify({
            "user_id": user_id,
            "predictions": predictions,
            "count": len(predictions)
        })
        
    except Exception as e:
        logger.error(f"User predictions error: {str(e)}")
        return jsonify({"error": "Failed to fetch user predictions"}), 500

@app.route('/analytics/trends', methods=['GET'])
def get_analytics_trends():
    """Get analytics trends over time"""
    try:
        metric_name = request.args.get('metric_name')
        days = int(request.args.get('days', 30))
        
        analytics = db_manager.get_analytics(metric_name, days)
        
        # Calculate trends
        if len(analytics) > 1:
            first_value = analytics[-1]['metric_value']
            last_value = analytics[0]['metric_value']
            trend = "increasing" if last_value > first_value else "decreasing" if last_value < first_value else "stable"
            change_percent = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
        else:
            trend = "insufficient_data"
            change_percent = 0
        
        return jsonify({
            "analytics": analytics,
            "trend": trend,
            "change_percent": round(change_percent, 2),
            "period_days": days,
            "count": len(analytics)
        })
        
    except Exception as e:
        logger.error(f"Analytics trends error: {str(e)}")
        return jsonify({"error": "Failed to fetch analytics trends"}), 500

if __name__ == "__main__":
    app.run(debug=True)