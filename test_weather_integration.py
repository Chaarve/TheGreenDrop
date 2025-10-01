#!/usr/bin/env python3
"""
Test script for IMD Weather API integration with GreenDrop
This script tests all the new weather endpoints and functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_LOCATIONS = [
    {"name": "Delhi", "lat": 28.6139, "lon": 77.2090, "city_id": 42182},
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "city_id": 43003},
    {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946, "city_id": 43295},
    {"name": "Chennai", "lat": 13.0827, "lon": 80.2707, "city_id": 43279}
]

def test_endpoint(endpoint, params=None, expected_status=200):
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🔍 Testing: {endpoint}")
        print(f"   URL: {url}")
        if params:
            print(f"   Params: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print("   ✅ SUCCESS")
            try:
                data = response.json()
                print(f"   Response keys: {list(data.keys())}")
                return data
            except:
                print("   Response: Non-JSON response")
                return response.text
        else:
            print(f"   ❌ FAILED - Expected {expected_status}, got {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ ERROR: {e}")
        return None

def test_weather_endpoints():
    """Test all weather-related endpoints"""
    print("=" * 60)
    print("🌤️  TESTING IMD WEATHER API INTEGRATION")
    print("=" * 60)
    
    # Test with Delhi location
    delhi = TEST_LOCATIONS[0]
    
    # 1. Test basic weather endpoint
    weather_data = test_endpoint("/weather", {
        "lat": delhi["lat"],
        "lon": delhi["lon"]
    })
    
    # 2. Test weather with city ID
    weather_data_city = test_endpoint("/weather", {
        "lat": delhi["lat"],
        "lon": delhi["lon"],
        "city_id": delhi["city_id"]
    })
    
    # 3. Test forecast endpoint
    forecast_data = test_endpoint("/weather/forecast", {
        "lat": delhi["lat"],
        "lon": delhi["lon"]
    })
    
    # 4. Test alerts endpoint
    alerts_data = test_endpoint("/weather/alerts", {
        "lat": delhi["lat"],
        "lon": delhi["lon"]
    })
    
    # 5. Test recharge metrics endpoint
    recharge_data = test_endpoint("/weather/recharge-metrics", {
        "lat": delhi["lat"],
        "lon": delhi["lon"]
    })
    
    # 6. Test cities list endpoint
    cities_data = test_endpoint("/weather/cities")
    
    return {
        "weather": weather_data,
        "weather_city": weather_data_city,
        "forecast": forecast_data,
        "alerts": alerts_data,
        "recharge": recharge_data,
        "cities": cities_data
    }

def test_prediction_with_weather():
    """Test the main prediction endpoint with weather integration"""
    print("\n" + "=" * 60)
    print("🚀 TESTING PREDICTION WITH WEATHER INTEGRATION")
    print("=" * 60)
    
    delhi = TEST_LOCATIONS[0]
    
    prediction_payload = {
        "latitude": delhi["lat"],
        "longitude": delhi["lon"],
        "roof_area_m2": 100,
        "roof_type": "Concrete",
        "available_space_m2": 120,
        "elevation_m": 216,
        "clay_pct": 30,
        "sand_pct": 40,
        "silt_pct": 30,
        "infiltration_rate_mmhr": 12,
        "runoff_coefficient": 0.85
    }
    
    try:
        print(f"\n🔍 Testing prediction endpoint")
        print(f"   Payload: {json.dumps(prediction_payload, indent=2)}")
        
        response = requests.post(f"{BASE_URL}/predict", 
                               json=prediction_payload, 
                               timeout=60)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS")
            data = response.json()
            
            print(f"   Prediction Results:")
            print(f"   - Feasibility Category: {data.get('feasibility_category')}")
            print(f"   - Feasibility Score: {data.get('feasibility_score')}")
            print(f"   - Recommended Structure: {data.get('recommended_structure')}")
            print(f"   - Tank Capacity: {data.get('recommended_tank_capacity_liters')}L")
            
            if 'weather_data' in data:
                weather = data['weather_data']
                print(f"   Weather Data:")
                print(f"   - Annual Rainfall: {weather.get('annual_rainfall_mm')}mm")
                print(f"   - Temperature: {weather.get('avg_temperature_c')}°C")
                print(f"   - Data Source: {weather.get('data_source')}")
                
                if 'monsoon_intensity' in weather:
                    monsoon = weather['monsoon_intensity']
                    print(f"   - Monsoon Intensity: {monsoon.get('monsoon_intensity')}")
            
            return data
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ ERROR: {e}")
        return None

def test_multiple_locations():
    """Test weather data for multiple locations"""
    print("\n" + "=" * 60)
    print("🌍 TESTING MULTIPLE LOCATIONS")
    print("=" * 60)
    
    results = {}
    
    for location in TEST_LOCATIONS:
        print(f"\n📍 Testing {location['name']} ({location['lat']}, {location['lon']})")
        
        # Test weather data
        weather = test_endpoint("/weather", {
            "lat": location["lat"],
            "lon": location["lon"],
            "city_id": location["city_id"]
        })
        
        # Test recharge metrics
        recharge = test_endpoint("/weather/recharge-metrics", {
            "lat": location["lat"],
            "lon": location["lon"]
        })
        
        results[location['name']] = {
            "weather": weather,
            "recharge": recharge
        }
        
        # Small delay between requests
        time.sleep(1)
    
    return results

def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n" + "=" * 60)
    print("🏥 TESTING HEALTH CHECK")
    print("=" * 60)
    
    health_data = test_endpoint("/health")
    
    if health_data:
        print(f"   Health Status: {health_data.get('status')}")
        print(f"   Timestamp: {health_data.get('timestamp')}")
        
        models = health_data.get('models_loaded', {})
        print(f"   Models Loaded:")
        for model, loaded in models.items():
            status = "✅" if loaded else "❌"
            print(f"   - {model}: {status}")
    
    return health_data

def generate_test_report(results):
    """Generate a comprehensive test report"""
    print("\n" + "=" * 60)
    print("📊 TEST REPORT SUMMARY")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    # Count tests
    for category, data in results.items():
        if isinstance(data, dict):
            for test_name, result in data.items():
                total_tests += 1
                if result is not None:
                    passed_tests += 1
        else:
            total_tests += 1
            if data is not None:
                passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed Tests: {passed_tests}")
    print(f"Failed Tests: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Overall Status: EXCELLENT")
    elif success_rate >= 60:
        print("✅ Overall Status: GOOD")
    elif success_rate >= 40:
        print("⚠️  Overall Status: NEEDS IMPROVEMENT")
    else:
        print("❌ Overall Status: POOR")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main test function"""
    print("🚀 Starting IMD Weather API Integration Tests")
    print(f"Target Server: {BASE_URL}")
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    try:
        # Test health endpoint first
        results['health'] = test_health_endpoint()
        
        # Test weather endpoints
        results['weather_endpoints'] = test_weather_endpoints()
        
        # Test prediction with weather integration
        results['prediction'] = test_prediction_with_weather()
        
        # Test multiple locations
        results['multiple_locations'] = test_multiple_locations()
        
        # Generate report
        generate_test_report(results)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
    
    print("\n🏁 Test execution completed")

if __name__ == "__main__":
    main()


