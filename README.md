# Kenyan Crop Recommendation System

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
source venv/bin/activate  # On Windows: venv\Scripts\activate
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
