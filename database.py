import sqlite3
import json
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "thegreendrop.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                latitude REAL,
                longitude REAL,
                roof_area_m2 REAL,
                roof_type TEXT,
                feasibility_category TEXT,
                feasibility_score REAL,
                recommended_structure TEXT,
                recommended_tank_capacity_liters INTEGER,
                weather_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create weather_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL,
                longitude REAL,
                annual_rainfall_mm REAL,
                max_daily_rainfall_mm REAL,
                rainy_days_count INTEGER,
                avg_temperature_c REAL,
                evaporation_rate_mmday REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value REAL,
                location TEXT,
                date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_prediction(self, prediction_data: Dict) -> int:
        """Save a prediction to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions 
            (user_id, latitude, longitude, roof_area_m2, roof_type, 
             feasibility_category, feasibility_score, recommended_structure, 
             recommended_tank_capacity_liters, weather_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction_data.get('user_id'),
            prediction_data.get('latitude'),
            prediction_data.get('longitude'),
            prediction_data.get('roof_area_m2'),
            prediction_data.get('roof_type'),
            prediction_data.get('feasibility_category'),
            prediction_data.get('feasibility_score'),
            prediction_data.get('recommended_structure'),
            prediction_data.get('recommended_tank_capacity_liters'),
            json.dumps(prediction_data.get('weather_data', {}))
        ))
        
        prediction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return prediction_id
    
    def get_predictions(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Retrieve predictions from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT * FROM predictions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM predictions 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Parse weather_data JSON
        for result in results:
            if result['weather_data']:
                result['weather_data'] = json.loads(result['weather_data'])
        
        conn.close()
        return results
    
    def save_weather_data(self, weather_data: Dict, latitude: float, longitude: float) -> int:
        """Save weather data to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO weather_data 
            (latitude, longitude, annual_rainfall_mm, max_daily_rainfall_mm, 
             rainy_days_count, avg_temperature_c, evaporation_rate_mmday)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            latitude,
            longitude,
            weather_data.get('annual_rainfall_mm'),
            weather_data.get('max_daily_rainfall_mm'),
            weather_data.get('rainy_days_count'),
            weather_data.get('avg_temperature_c'),
            weather_data.get('evaporation_rate_mmday')
        ))
        
        weather_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return weather_id
    
    def get_weather_data(self, latitude: float, longitude: float, days: int = 30) -> List[Dict]:
        """Get recent weather data for a location"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM weather_data 
            WHERE latitude = ? AND longitude = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (latitude, longitude, days))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def save_analytics(self, metric_name: str, metric_value: float, location: str = None) -> int:
        """Save analytics data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analytics (metric_name, metric_value, location, date)
            VALUES (?, ?, ?, ?)
        ''', (metric_name, metric_value, location, datetime.now().date()))
        
        analytics_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return analytics_id
    
    def get_analytics(self, metric_name: str = None, days: int = 30) -> List[Dict]:
        """Get analytics data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if metric_name:
            cursor.execute('''
                SELECT * FROM analytics 
                WHERE metric_name = ? AND date >= date('now', '-{} days')
                ORDER BY date DESC
            '''.format(days), (metric_name,))
        else:
            cursor.execute('''
                SELECT * FROM analytics 
                WHERE date >= date('now', '-{} days')
                ORDER BY date DESC
            '''.format(days))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total predictions
        cursor.execute('SELECT COUNT(*) FROM predictions')
        total_predictions = cursor.fetchone()[0]
        
        # Predictions today
        cursor.execute('SELECT COUNT(*) FROM predictions WHERE date(created_at) = date("now")')
        today_predictions = cursor.fetchone()[0]
        
        # Average feasibility score
        cursor.execute('SELECT AVG(feasibility_score) FROM predictions')
        avg_score = cursor.fetchone()[0] or 0
        
        # Most common roof type
        cursor.execute('SELECT roof_type, COUNT(*) as count FROM predictions GROUP BY roof_type ORDER BY count DESC LIMIT 1')
        most_common_roof = cursor.fetchone()
        
        # Average tank capacity
        cursor.execute('SELECT AVG(recommended_tank_capacity_liters) FROM predictions')
        avg_tank_capacity = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_predictions': total_predictions,
            'today_predictions': today_predictions,
            'average_feasibility_score': round(avg_score, 2),
            'most_common_roof_type': most_common_roof[0] if most_common_roof else 'N/A',
            'average_tank_capacity': round(avg_tank_capacity, 0)
        }
    
    def export_data(self, table_name: str) -> pd.DataFrame:
        """Export data from a specific table as DataFrame"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df


