"""
Application Configuration
"""

import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MODEL_PATH = os.path.join('models', 'trained', 'crop_recommendation_model.pkl')
    NUTRIENT_REQUIREMENTS_PATH = os.path.join('models', 'trained', 'nutrient_requirements.json')
    
    # API Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    
    # Kenya boundaries for validation
    KENYA_LAT_MIN = -4.6795
    KENYA_LAT_MAX = 5.0332
    KENYA_LON_MIN = 33.9098
    KENYA_LON_MAX = 41.8992
