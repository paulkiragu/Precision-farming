"""
Data Fetcher Module
Handles API calls and heuristic conversions
- Nominatim API: Location to coordinates
- Open-Meteo API: Real-time weather data
- Visual Soil Heuristic: Soil type to nutrient mapping
"""

import requests
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class DataFetcher:
    """Handles external data fetching and heuristic mappings"""
    
    # Visual Heuristic for Soil Nutrients (Based on KALRO regional data)
    SOIL_HEURISTIC_MAP = {
        'Red Volcanic': {'N': 60, 'P': 20, 'K': 40, 'pH': 5.5},
        'Black Cotton': {'N': 70, 'P': 25, 'K': 45, 'pH': 6.8},
        'Loam': {'N': 50, 'P': 30, 'K': 35, 'pH': 6.5},
        'Sandy Loam': {'N': 30, 'P': 15, 'K': 25, 'pH': 6.0},
        'Clay Loam': {'N': 65, 'P': 28, 'K': 50, 'pH': 6.7},
        'Silty Loam': {'N': 55, 'P': 25, 'K': 40, 'pH': 6.3},
        'Clay': {'N': 60, 'P': 22, 'K': 55, 'pH': 7.0},
        'Silty Clay': {'N': 58, 'P': 24, 'K': 48, 'pH': 6.6},
    }
    
    def get_location_coordinates(self, location_name: str) -> Optional[Dict]:
        """Convert location name to coordinates using Nominatim API"""
        try:
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': f"{location_name}, Kenya",
                'format': 'json',
                'limit': 1
            }
            headers = {'User-Agent': 'CropRecommendation/1.0'}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data:
                return {
                    'lat': float(data[0]['lat']),
                    'lon': float(data[0]['lon'])
                }
        except Exception as e:
            logger.error(f"Error fetching location: {e}")
        return None
    
    def get_weather_data(self, lat: float, lon: float) -> Optional[Dict]:
        """Fetch weather data from Open-Meteo API"""
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'current_weather': True,
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
                'timezone': 'Africa/Nairobi'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
        return None
    
    def map_soil_to_nutrients(self, soil_type: str) -> Dict:
        """Map visual soil type to nutrient values using heuristic"""
        return self.SOIL_HEURISTIC_MAP.get(soil_type, self.SOIL_HEURISTIC_MAP['Loam'])
