"""
Project Structure Setup Script
Purpose: Create industry-standard folder structure for Kenyan Crop Recommendation System
Based on: Project Guidelines PDF + Proposal Document
Standard: Follows Flask/React best practices + Data Science project structure
Date: December 15, 2025
"""

import os
import shutil

def create_directory(path, description=""):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"  ✓ Created: {path}")
        if description:
            print(f"    └─ {description}")
    else:
        print(f"  ○ Exists: {path}")

def create_file(path, content="", description=""):
    """Create file with optional content"""
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(content)
        print(f"  ✓ Created: {path}")
        if description:
            print(f"    └─ {description}")
    else:
        print(f"  ○ Exists: {path}")

print("=" * 80)
print("KENYAN CROP RECOMMENDATION SYSTEM - PROJECT STRUCTURE SETUP")
print("=" * 80)

# Get project root
project_root = os.getcwd()
print(f"\nProject Root: {project_root}\n")

# ============================================================================
# PHASE 1: ROOT LEVEL STRUCTURE
# ============================================================================
print("[PHASE 1] Creating Root Level Structure...")
print("-" * 80)

# Core directories
directories = {
    # Backend (Flask API)
    "backend": "Flask backend application",
    "backend/app": "Main Flask application package",
    "backend/app/routes": "API route handlers",
    "backend/app/models": "Data models and ML model integration",
    "backend/app/utils": "Utility functions and helpers",
    "backend/app/config": "Configuration files",
    "backend/app/static": "Static files (CSS, JS, images)",
    "backend/app/templates": "HTML templates",
    
    # Frontend (React)
    "frontend": "React frontend application",
    "frontend/public": "Public assets",
    "frontend/src": "React source code",
    "frontend/src/components": "React components",
    "frontend/src/pages": "Page components",
    "frontend/src/services": "API service calls",
    "frontend/src/utils": "Utility functions",
    "frontend/src/styles": "CSS/Tailwind styles",
    
    # Data (as per guidelines)
    "data": "All datasets and data-related files",
    "data/raw": "Original unprocessed datasets",
    "data/processed": "Cleaned and processed datasets",
    "data/external": "External data sources (KALRO, Meteorological)",
    
    # Models (as per guidelines)
    "models": "Trained ML models and related files",
    "models/trained": "Serialized trained models (.pkl files)",
    "models/experiments": "Model training experiments and logs",
    
    # Notebooks (Data Science workflow)
    "notebooks": "Jupyter notebooks for exploration and analysis",
    "notebooks/01_exploratory": "Exploratory Data Analysis (EDA)",
    "notebooks/02_preprocessing": "Data preprocessing experiments",
    "notebooks/03_modeling": "Model training and evaluation",
    "notebooks/04_visualization": "Data visualization notebooks",
    
    # Scripts (Automation and utilities)
    "scripts": "Utility scripts and automation",
    "scripts/data_processing": "Data processing scripts",
    "scripts/model_training": "Model training scripts",
    "scripts/deployment": "Deployment scripts",
    
    # Tests (Unit and integration tests)
    "tests": "Test suite",
    "tests/unit": "Unit tests",
    "tests/integration": "Integration tests",
    "tests/fixtures": "Test fixtures and mock data",
    
    # Documentation
    "docs": "Project documentation",
    "docs/api": "API documentation",
    "docs/user_guide": "User guides and manuals",
    "docs/technical": "Technical documentation",
    "docs/images": "Documentation images and diagrams",
    
    # Configuration
    "config": "Project-wide configuration files",
    
    # Logs
    "logs": "Application logs",
    
    # Deployment
    "deployment": "Deployment configurations",
    "deployment/docker": "Docker configurations",
    "deployment/nginx": "Nginx configurations",
}

for dir_path, description in directories.items():
    create_directory(dir_path, description)

print()

# ============================================================================
# PHASE 2: BACKEND FILES (Flask Application)
# ============================================================================
print("[PHASE 2] Creating Backend Files...")
print("-" * 80)

# app.py (Main Flask application)
app_py_content = '''"""
Main Flask Application
Manages routes and connects frontend to AI model
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from backend.app.config.settings import Config
import logging

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for React frontend
    CORS(app)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Register blueprints
    from backend.app.routes import main_routes, api_routes
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(api_routes.bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

# data_fetcher.py (API calls and heuristic conversions)
data_fetcher_content = '''"""
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
'''

# settings.py (Configuration)
settings_content = '''"""
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
'''

backend_files = {
    "backend/app.py": app_py_content,
    "backend/app/__init__.py": "# Flask app package",
    "backend/app/routes/__init__.py": "# Routes package",
    "backend/app/models/__init__.py": "# Models package",
    "backend/app/utils/__init__.py": "# Utils package",
    "backend/app/utils/data_fetcher.py": data_fetcher_content,
    "backend/app/config/__init__.py": "# Config package",
    "backend/app/config/settings.py": settings_content,
    "backend/requirements.txt": '''flask==2.3.0
flask-cors==4.0.0
scikit-learn==1.2.0
pandas==1.5.3
numpy==1.24.0
requests==2.31.0
python-dotenv==1.0.0
gunicorn==20.1.0
''',
}

for file_path, content in backend_files.items():
    create_file(file_path, content)

print()

# ============================================================================
# PHASE 3: FRONTEND FILES (React Application)
# ============================================================================
print("[PHASE 3] Creating Frontend Files...")
print("-" * 80)

package_json = '''{
  "name": "crop-recommendation-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.4.0",
    "react-router-dom": "^6.14.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "devDependencies": {
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.14",
    "postcss": "^8.4.24"
  }
}
'''

frontend_files = {
    "frontend/package.json": package_json,
    "frontend/README.md": "# Crop Recommendation Frontend\n\nReact + Tailwind CSS application",
    "frontend/.gitignore": "node_modules/\nbuild/\n.env",
    "frontend/public/index.html": "<!DOCTYPE html><html><head><title>Smart Crop Advisor</title></head><body><div id='root'></div></body></html>",
    "frontend/src/index.js": "// React entry point",
    "frontend/src/App.js": "// Main App component",
}

for file_path, content in frontend_files.items():
    create_file(file_path, content)

print()

# ============================================================================
# PHASE 4: PROJECT ROOT FILES
# ============================================================================
print("[PHASE 4] Creating Root Configuration Files...")
print("-" * 80)

readme_content = '''# Kenyan Crop Recommendation System

## Overview
An intelligent crop-selection algorithm and growth guidance system tailored to Kenyan agro-ecological zones.

## Features
- Machine Learning-based crop recommendations
- Real-time weather integration (Open-Meteo API)
- Visual soil heuristic mapping
- Nutrient gap analysis
- User-friendly web interface

## Project Structure
```
precisionfarming/
├── backend/          # Flask API
├── frontend/         # React UI
├── data/            # Datasets
├── models/          # ML models
├── notebooks/       # Jupyter notebooks
├── scripts/         # Utility scripts
├── tests/           # Test suite
└── docs/            # Documentation
```

## Setup Instructions

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Technology Stack
- **Backend**: Python 3.10, Flask 2.3
- **Frontend**: React 18, Tailwind CSS 3.3
- **ML**: Scikit-learn 1.2
- **APIs**: Open-Meteo, Nominatim

## Authors
- Project Team

## License
Educational Project
'''

gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/
dist/
build/

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local

# Logs
logs/
*.log

# Data (large files)
data/raw/*.csv
data/external/*.csv

# Models (large files)
models/trained/*.pkl
models/experiments/

# Node
node_modules/
build/
.npm

# Testing
.coverage
htmlcov/
.pytest_cache/
'''

dockerfile_content = '''FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY models/ ./models/
COPY data/processed/ ./data/processed/

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:create_app()"]
'''

docker_compose_content = '''version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./logs:/app/logs

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
'''

root_files = {
    "README.md": readme_content,
    ".gitignore": gitignore_content,
    "Dockerfile": dockerfile_content,
    "docker-compose.yml": docker_compose_content,
    "requirements.txt": "# Root requirements - use backend/requirements.txt",
    ".env.example": "SECRET_KEY=your-secret-key\nFLASK_ENV=development",
}

for file_path, content in root_files.items():
    create_file(file_path, content)

print()

# ============================================================================
# PHASE 5: MOVE EXISTING FILES TO APPROPRIATE LOCATIONS
# ============================================================================
print("[PHASE 5] Organizing Existing Files...")
print("-" * 80)

file_moves = {
    # Move datasets
    "combined_smartgrow_dataset.csv": "data/raw/combined_smartgrow_dataset.csv",
    "Crop_recommendation_dataset.csv": "data/raw/Crop_recommendation_dataset.csv",
    "smartgrow_cleaned.csv": "data/processed/smartgrow_cleaned.csv",
    "crop_recommendation_cleaned.csv": "data/processed/crop_recommendation_cleaned.csv",
    "High_Accuracy_Crop_Data.csv": "data/processed/High_Accuracy_Crop_Data.csv",
    
    # Move documentation
    "project_guideline.pdf": "docs/project_guideline.pdf",
    "Proposal paul.docx": "docs/Proposal_paul.docx",
    
    # Move scripts
    "data_cleaning.py": "scripts/data_processing/data_cleaning.py",
}

for src, dest in file_moves.items():
    if os.path.exists(src):
        try:
            shutil.move(src, dest)
            print(f"  ✓ Moved: {src} → {dest}")
        except Exception as e:
            print(f"  ✗ Error moving {src}: {e}")
    else:
        print(f"  ○ Not found: {src}")

print()

# ============================================================================
# PHASE 6: CREATE PLACEHOLDER FILES
# ============================================================================
print("[PHASE 6] Creating Placeholder Files...")
print("-" * 80)

placeholder_files = {
    "models/trained/.gitkeep": "# Trained models directory",
    "data/external/.gitkeep": "# External data directory",
    "logs/.gitkeep": "# Logs directory",
    "notebooks/01_exploratory/01_data_exploration.ipynb": "# EDA notebook placeholder",
    "tests/unit/test_model.py": "# Unit tests for model",
    "tests/integration/test_api.py": "# Integration tests for API",
    "docs/api/endpoints.md": "# API Documentation\n\n## Endpoints\n- POST /api/predict - Get crop recommendation",
}

for file_path, content in placeholder_files.items():
    create_file(file_path, content)

print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("=" * 80)
print("PROJECT STRUCTURE SETUP COMPLETED!")
print("=" * 80)

print("\n📁 Directory Structure Created:")
print("""
precisionfarming/
├── backend/                    # Flask Backend
│   ├── app/
│   │   ├── routes/            # API routes
│   │   ├── models/            # Model integration
│   │   ├── utils/             # Data fetcher, helpers
│   │   ├── config/            # Settings
│   │   ├── static/            # Static files
│   │   └── templates/         # HTML templates
│   ├── app.py                 # Main Flask app
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   └── utils/             # Utilities
│   └── package.json           # Node dependencies
│
├── data/                       # Datasets
│   ├── raw/                   # Original datasets
│   ├── processed/             # Cleaned datasets
│   └── external/              # KALRO, Met data
│
├── models/                     # ML Models
│   ├── trained/               # .pkl files
│   └── experiments/           # Training logs
│
├── notebooks/                  # Jupyter Notebooks
│   ├── 01_exploratory/        # EDA
│   ├── 02_preprocessing/      # Data prep
│   ├── 03_modeling/           # Model training
│   └── 04_visualization/      # Visualizations
│
├── scripts/                    # Automation Scripts
│   ├── data_processing/       # Data scripts
│   ├── model_training/        # Training scripts
│   └── deployment/            # Deployment scripts
│
├── tests/                      # Test Suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test data
│
├── docs/                       # Documentation
│   ├── api/                   # API docs
│   ├── user_guide/            # User guides
│   ├── technical/             # Technical docs
│   └── images/                # Diagrams
│
├── deployment/                 # Deployment
│   ├── docker/                # Docker configs
│   └── nginx/                 # Nginx configs
│
├── config/                     # Project configs
├── logs/                       # Application logs
├── venv/                       # Virtual environment
│
├── README.md                   # Project overview
├── .gitignore                 # Git ignore rules
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose
└── requirements.txt           # Root dependencies
""")

print("\n✅ Next Steps:")
print("  1. Review the created structure")
print("  2. Install backend dependencies: cd backend && pip install -r requirements.txt")
print("  3. Install frontend dependencies: cd frontend && npm install")
print("  4. Start developing in notebooks/01_exploratory/")
print("  5. Train model and save to models/trained/")
print("  6. Implement API endpoints in backend/app/routes/")
print("  7. Build React UI in frontend/src/")
print("\n" + "=" * 80)
