# 🌧️ TheGreenDrop – Smart Rainwater Harvesting Management System

## Overview
TheGreenDrop is an innovative Smart Rainwater Harvesting Management System designed to optimize rainwater collection, storage, and usage through advanced forecasting and AI-driven recommendations. This project aims to promote sustainable water management practices by leveraging technology to enhance the efficiency of rainwater harvesting systems.

## ✨ Features

### 🤖 **Machine Learning & AI**
- **Advanced ML Pipeline**: Enhanced Random Forest models with ensemble methods
- **Feature Engineering**: 7+ derived features for better predictions
- **Hyperparameter Tuning**: Optimized model performance with GridSearchCV
- **Real-time Predictions**: Instant feasibility analysis and recommendations

### 🌤️ **Weather Integration**
- **Multi-source Weather Data**: IMD API + OpenWeatherMap fallback
- **Real-time Weather**: Current conditions and historical data
- **Location-based Analysis**: GPS coordinates for accurate predictions
- **Climate Factors**: Temperature, evaporation, and rainfall patterns

### 🎨 **Modern User Interface**
- **React Vite Frontend**: Fast, modern, and responsive
- **Interactive Forms**: Smart form with location detection
- **Data Visualization**: Charts and graphs with Recharts
- **Real-time Updates**: Live weather data and predictions

### 💾 **Database & Analytics**
- **SQLite Database**: Lightweight, serverless data storage
- **Prediction History**: Track all user predictions
- **Analytics Dashboard**: Usage statistics and insights
- **Data Export**: Export data for further analysis

### 🔧 **API & Backend**
- **Flask REST API**: Comprehensive backend with multiple endpoints
- **CORS Enabled**: Cross-origin requests supported
- **Error Handling**: Robust error management and logging
- **Health Monitoring**: System health and model status checks

## 🏗️ **Project Structure**

```
GreenDrop/
├── TheGreenDrop/                    # Flask Backend
│   ├── api.py                      # Main Flask API
│   ├── ml_pipeline.py              # Enhanced ML pipeline
│   ├── database.py                 # Database operations
│   ├── run_server.py               # Server startup script
│   ├── requirements.txt            # Python dependencies
│   ├── *.joblib                    # Trained ML models
│   └── *.csv                       # Training data
├── thegreendrop-vite/              # React Frontend
│   ├── src/
│   │   ├── App.jsx                 # Main app component
│   │   ├── WaterPredictionForm.jsx # Prediction form
│   │   └── App.css                 # Styling
│   ├── package.json                # Frontend dependencies
│   ├── vite.config.js              # Vite configuration
│   └── run_frontend.js             # Frontend startup script
└── README.md                       # This file
```

## 🚀 **Quick Start**

### Prerequisites
- Python 3.8+ 
- Node.js 16+
- npm or yarn

### 1. **Backend Setup (Flask API)**

```bash
# Navigate to backend directory
cd TheGreenDrop

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Train ML models (first time only)
python ml_pipeline.py

# Start Flask server
python run_server.py
```

The API will be available at: `http://localhost:5000`

### 2. **Frontend Setup (React Vite)**

```bash
# Navigate to frontend directory
cd thegreendrop-vite

# Install dependencies
npm install

# Start development server
npm run dev
# OR use the startup script
node run_frontend.js
```

The frontend will be available at: `http://localhost:5173`

## 📊 **API Endpoints**

### Core Endpoints
- `POST /predict` - Get rainwater harvesting prediction
- `GET /weather` - Get weather data for location
- `GET /health` - System health check

### Database Endpoints
- `GET /predictions` - Get prediction history
- `GET /dashboard` - Get dashboard statistics
- `GET /analytics` - Get analytics data
- `GET /export/<table>` - Export data

### Example API Usage

```bash
# Get prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 28.6139,
    "longitude": 77.2090,
    "roof_area_m2": 100,
    "roof_type": "Concrete"
  }'

# Get weather data
curl "http://localhost:5000/weather?lat=28.6139&lon=77.2090"

# Get dashboard stats
curl "http://localhost:5000/dashboard"
```

## 🔧 **Configuration**

### Environment Variables
Create a `.env` file in the `TheGreenDrop` directory:

```env
# Weather API Configuration
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///thegreendrop.db

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### Weather API Setup
1. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Add the key to your `.env` file
3. For IMD API, check the provided PDF documentation

## 📈 **ML Pipeline Features**

### Enhanced Features
- **Derived Features**: 7 additional calculated features
- **Ensemble Methods**: Voting regressor for better accuracy
- **Hyperparameter Tuning**: GridSearchCV optimization
- **Feature Importance**: Analysis of most important features
- **Cross-validation**: 5-fold CV for robust evaluation

### Model Performance
- **Classification**: Feasibility category prediction
- **Regression**: Feasibility score (0-10 scale)
- **Recommendation**: Optimal structure type
- **Metrics**: RMSE, R², MAE, Accuracy

## 🎨 **Frontend Features**

### User Experience
- **Location Detection**: Automatic GPS coordinates
- **Real-time Weather**: Live weather data display
- **Interactive Forms**: Smart form with validation
- **Responsive Design**: Works on all devices
- **Data Visualization**: Charts and graphs

### Components
- **WaterPredictionForm**: Main prediction interface
- **Weather Display**: Current weather information
- **Results Visualization**: Charts and recommendations
- **Monthly Breakdown**: Water harvest by month

## 💾 **Database Schema**

### Tables
- **predictions**: User predictions and results
- **weather_data**: Historical weather information
- **analytics**: System metrics and statistics
- **users**: User information (optional)

### Data Export
Export data in JSON format for analysis:
```bash
curl "http://localhost:5000/export/predictions"
curl "http://localhost:5000/export/analytics"
```

## 🔍 **Troubleshooting**

### Common Issues

1. **Models not found**
   ```bash
   cd TheGreenDrop
   python ml_pipeline.py
   ```

2. **Dependencies missing**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

3. **CORS errors**
   - Ensure Flask server is running on port 5000
   - Check Vite proxy configuration

4. **Weather API errors**
   - Verify API key is correct
   - Check internet connection
   - API has fallback to default values

### Logs
- Flask logs: Check console output
- Database logs: SQLite database in `TheGreenDrop/`
- Frontend logs: Browser console

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License. See the LICENSE file for details.

## 🙏 **Acknowledgments**

- India Meteorological Department (IMD) for weather data
- OpenWeatherMap for weather API
- Scikit-learn for machine learning
- React and Vite for frontend framework
- Flask for backend framework

---

**🌧️ TheGreenDrop - Making Rainwater Harvesting Smart and Sustainable!**