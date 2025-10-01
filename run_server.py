#!/usr/bin/env python3
"""
TheGreenDrop Server Startup Script
This script starts the Flask API server with proper configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import pandas
        import numpy
        import sklearn
        import joblib
        import requests
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def check_models():
    """Check if ML models exist"""
    model_files = [
        "feasibility_category_model.joblib",
        "feasibility_score_model.joblib", 
        "recommended_structure_model.joblib",
        "scaler.joblib",
        "model_features.joblib"
    ]
    
    missing_models = []
    for model_file in model_files:
        if not Path(model_file).exists():
            missing_models.append(model_file)
    
    if missing_models:
        print("❌ Missing ML models:")
        for model in missing_models:
            print(f"   - {model}")
        print("\nPlease run: python ml_pipeline.py")
        return False
    
    print("✅ All ML models found")
    return True

def setup_environment():
    """Setup environment variables"""
    # Set default environment variables
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', 'True')
    os.environ.setdefault('OPENWEATHER_API_KEY', 'your_openweather_api_key_here')
    
    print("✅ Environment configured")

def main():
    """Main startup function"""
    print("🌧️ TheGreenDrop Server Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check models
    if not check_models():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    print("\n🚀 Starting Flask server...")
    print("Server will be available at: http://localhost:5000")
    print("API Documentation: http://localhost:5000/health")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 40)
    
    # Start the Flask server
    try:
        from api import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


