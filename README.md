# AI-POWERED PRECISION AGRICULTURE SYSTEM FOR LOCATION-BASED CROP RECOMMENDATION USING RANDOM FOREST AND REAL-REAL WEATHER ANALYTICS

An intelligent crop-selection algorithm and growth guidance system tailored to Kenyan agro-ecological zones. This project leverages machine learning and real-time weather data to provide data-driven crop recommendations and growth guidance for farmers in Kenya.



## 🌾 Overview

This project provides an intelligent crop recommendation system specifically designed for Kenyan farmers. It uses machine learning models trained on crop data combined with real-time weather integration to suggest the most suitable crops for specific locations and soil conditions.

### Key Use Cases
- **Farmers**: Get data-driven crop recommendations based on their location and soil type
- **Agricultural Advisors**: Provide evidence-based guidance to farmers
- **Agricultural Organizations**: Monitor and optimize crop selection across regions

---

## ✨ Features

- **🤖 ML-Based Crop Recommendations**: Uses trained scikit-learn models to recommend suitable crops
- **🌤️ Real-Time Weather Integration**: Fetches current and forecast weather data using Open-Meteo API
- **📍 Geolocation Services**: Reverse geocoding with Nominatim for location-based recommendations
- **🌍 Climate Correction**: Kenya-specific climate adjustments for accurate predictions
- **💾 Soil Analysis**: Heuristic-based soil evaluation with nutrient gap analysis
- **🎨 Intuitive Web Interface**: Modern React UI with Tailwind CSS for user-friendly experience
- **📊 Data Visualization**: Visual representation of soil properties and recommendations
- **🔄 Responsive Design**: Works seamlessly on desktop and mobile devices

---

## 🖥️ System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows 10/11
- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: 5GB for all dependencies and data
- **Internet**: Required for weather API and geolocation services

### Hardware Setup
- **CPU**: Dual-core processor or better
- **Connection**: Stable internet connection required

---

## 📦 Installation Method


### Method 1: Manual Installation (Local Development)



**Prerequisites:**
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/) with npm or pnpm
- [Git](https://git-scm.com/)

**Step 1: Clone the Repository**

```bash
git clone <repository-url>
cd precisionfarming
```

**Step 2: Backend Setup**

```bash
cd backend

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask; print(f'Flask {flask.__version__}')"
```

**Step 3: Frontend Setup**

```bash
cd ../frontend

# Install dependencies
npm install
# Or with pnpm:
# pnpm install

# Verify installation
npm --version && node --version
```

---

### Method 2: Using Shell Scripts (Semi-Automated)

Quick setup scripts are provided for convenience (Linux/macOS/WSL).

```bash
# Start the backend API
./start_api.sh

# In another terminal, start the frontend
./start_mobile.sh
```

---

## 🚀 Quick Start


**Terminal 1 - Start Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
# Backend running at http://localhost:5000
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
# Frontend running at http://localhost:5173 (dev) or http://localhost:3000 (production)
```

### Option C: Shell Scripts

```bash
# Terminal 1
./start_api.sh

# Terminal 2
./start_mobile.sh
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cd backend
touch .env
```

Add the following variables (defaults are used if not specified):

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-secret-key-here

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# External APIs
OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1
NOMINATIM_BASE_URL=https://nominatim.openstreetmap.org

# Logging
LOG_LEVEL=INFO
LOG_DIR=./logs

# Optional: Cache Configuration
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300
```

### Data Files

The system uses pre-trained models and datasets located in:
- `models/trained/` - Pre-trained ML models and mappings
- `data/processed/` - Processed crop data
- `data/raw/` - Raw datasets

These files are included in the repository and require no additional setup.

---

## 🏃 Running the Project

```

#### With Manual Installation:

Open two terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

Expected output:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: off
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Expected output:
```
VITE v7.2.4 ready in 245 ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

### Verifying Installation

Check that both services are running:

```bash
# Test Backend API
curl http://localhost:5000/api/health

# Test Frontend (visit in browser)
# http://localhost:3000 (Docker/production)
# http://localhost:5173 (Development Vite)
```

---

## 📁 Project Structure

```
precisionfarming/
├── backend/                          # Flask REST API
│   ├── app.py                       # Main application entry point
│   ├── requirements.txt             # Python dependencies
│   ├── app/
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py          # Configuration management
│   │   ├── models/
│   │   │   └── predictor.py         # ML prediction logic
│   │   ├── routes/
│   │   │   └── api_routes.py        # API endpoints
│   │   ├── services/                # Business logic services
│   │   │   ├── api_integrator.py    # External API integration
│   │   │   ├── cache_manager.py     # Caching logic
│   │   │   ├── crop_guidance.py     # Crop guidance logic
│   │   │   ├── geocoding_service.py # Geolocation services
│   │   │   ├── kenya_climate_corrector.py  # Climate adjustments
│   │   │   ├── soil_heuristic.py    # Soil analysis
│   │   │   ├── weather_service.py   # Weather data fetching
│   │   │   └── api_integrator.py
│   │   ├── utils/
│   │   │   └── data_fetcher.py      # Data utilities
│   │   └── data/
│   │       └── crop_guidance.json   # Crop guidance rules
│   └── logs/                         # Application logs
│
├── frontend/                         # React Web Application
│   ├── src/
│   │   ├── App.jsx                  # Root component
│   │   ├── main.jsx                 # Entry point
│   │   ├── index.css                # Global styles
│   │   ├── pages/                   # Page components
│   │   │   ├── HomePage.jsx
│   │   │   ├── GuidancePage.jsx
│   │   │   └── ResultsPage.jsx
│   │   ├── components/              # Reusable components
│   │   ├── services/
│   │   │   └── api.js               # API client
│   │   ├── constants/
│   │   └── lib/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── data/
│   ├── raw/                         # Raw datasets
│   │   ├── combined_smartgrow_dataset.csv
│   │   └── Crop_recommendation_dataset.csv
│   └── processed/                   # Processed/cleaned data
│       └── High_Accuracy_Crop_Data_Enhanced.csv
│
├── models/
│   ├── trained/                     # Pre-trained ML models
│   │   ├── feature_names.json
│   │   ├── nutrient_requirements.json
│   │   └── soil_type_mapping.json
│   └── experiments/                 # Model experiments & visualizations
│
├── scripts/
│   ├── data_processing/             # Data preparation scripts
│   │   └── data_cleaning.py
│   └── model_training/              # Model training scripts
│       └── train_model.py
│
├── deployment/                      # Deployment configurations
│   ├── docker/
│   └── nginx/
│
├── docker-compose.yml               # Docker composition
├── Dockerfile                       # Backend Docker image
├── .dockerignore
├── README.md                        # This file
└── requirements.txt                 # Python dependencies
```

---

## 🛠️ Technology Stack

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Flask | 2.3 |
| Web Server | Gunicorn | 20.1 |
| ML Library | Scikit-learn | 1.2 |
| Data Processing | Pandas | 1.5.3 |
| Numerical | NumPy | 1.24 |
| HTTP Client | Requests | 2.31 |
| Configuration | Python-dotenv | 1.0 |
| CORS | Flask-CORS | 4.0 |
| Python Version | Python | 3.10+ |

### Frontend
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | React | 19.2 |
| Bundler | Vite | 7.2.4 |
| Styling | Tailwind CSS | 3.4 |
| HTTP Client | Axios | 1.13 |
| Forms | React Hook Form | 7.68 |
| UI Components | Radix UI | Latest |
| Icons | Lucide React | 0.561 |
| Animation | Framer Motion | 12.23 |
| Node Version | Node.js | 18+ |

### DevOps
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (reverse proxy)
- **Version Control**: Git

### External APIs
- **Weather**: Open-Meteo API (free, no authentication required)
- **Geolocation**: Nominatim/OpenStreetMap (free, no authentication required)

---

## 📡 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### Health Check
```http
GET /api/health
```
Returns API health status.

**Request:**
```bash
curl http://localhost:5000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

#### Get Crop Recommendations
```http
POST /api/recommendations
```
Get crop recommendations based on location and soil type.

**Request Body:**
```json
{
  "latitude": -1.2921,
  "longitude": 36.8219,
  "soil_type": "loamy",
  "season": "rainy"
}
```

**Response:**
```json
{
  "location": "Nairobi",
  "recommendations": [
    {
      "crop": "Maize",
      "suitability": 0.92,
      "confidence": "high"
    },
    {
      "crop": "Beans",
      "suitability": 0.85,
      "confidence": "high"
    }
  ],
  "weather": {
    "temperature": 25.3,
    "rainfall": 120,
    "humidity": 65
  }
}
```

---

#### Get Growth Guidance
```http
POST /api/guidance
```
Get detailed growth guidance for a selected crop.

**Request Body:**
```json
{
  "crop": "Maize",
  "location": {
    "latitude": -1.2921,
    "longitude": 36.8219
  },
  "soil_type": "loamy"
}
```

**Response:**
```json
{
  "crop": "Maize",
  "guidance": {
    "planting_period": "March-May",
    "watering_frequency": "Every 5-7 days",
    "nutrients": {
      "nitrogen": "150 kg/ha",
      "phosphorus": "100 kg/ha"
    },
    "expected_yield": "5-8 tons/ha"
  }
}
```

For complete API documentation, see [docs/API.md](docs/API.md) if available.

---

## 🔧 Troubleshooting

### Common Issues and Solutions


#### 1. Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find and kill process using port 5000 (backend)
# On Linux/macOS:
lsof -i :5000
kill -9 <PID>

# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or use different ports:
# Change in docker-compose.yml or .env
```

---

#### 2. Python Module Not Found

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
cd backend

# Verify virtual environment is activated
# Linux/macOS: check for (venv) prefix in prompt
# Windows: check for (venv) prefix in prompt

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify Flask installation
python -c "import flask; print(flask.__version__)"
```

---

#### 3. Frontend Won't Connect to Backend

**Error:** `Network Error` or `CORS error`

**Solution:**
```bash
# 1. Verify backend is running
curl http://localhost:5000/api/health

# 2. Check CORS configuration
# In backend/.env, ensure:
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# 3. Check API endpoint in frontend
# In frontend/src/services/api.js, verify:
# const API_BASE_URL = 'http://localhost:5000/api'

# 4. Restart both services
```

---

#### 4. Npm Install Issues

**Error:** `npm ERR! code ERESOLVE`

**Solution:**
```bash
cd frontend

# Use legacy peer deps
npm install --legacy-peer-deps

# Or use pnpm (alternative package manager)
npm install -g pnpm
pnpm install
```

---

#### 5. Weather API Rate Limiting

**Error:** `429 Too Many Requests`

**Solution:**
- Open-Meteo has rate limits (10,000 requests/day for free tier)
- Implement caching (already done in `cache_manager.py`)
- Check cache configuration in `.env`

---

#### 6. Dataset Loading Issues

**Error:** `FileNotFoundError: data/processed/...csv`

**Solution:**
```bash
# Ensure data files exist
ls -la data/raw/
ls -la data/processed/

# If missing, run data processing script
python scripts/data_processing/data_cleaning.py
```

---

### Getting More Help

- **Check Logs**: 
  ```bash
  # Docker logs
  docker-compose logs backend
  docker-compose logs frontend
  
  # Local logs
  tail -f backend/logs/app.log
  ```

- **Check API Responses**:
  ```bash
  # Test API endpoint
  curl -X POST http://localhost:5000/api/recommendations \
    -H "Content-Type: application/json" \
    -d '{"latitude": -1.2921, "longitude": 36.8219}'
  ```

---

## 👨‍💻 Development Workflow

### Setting Up Development Environment

#### Backend Development

```bash
cd backend
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt

# Run with debug mode
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

#### Frontend Development

```bash
cd frontend

# Run development server with hot reload
npm run dev

# Run linting
npm run lint

# Build for production
npm run build
```

### Making Code Changes

**Backend:**
1. Modify files in `backend/app/`
2. Changes auto-reload in debug mode
3. Test with curl or Postman

**Frontend:**
1. Modify files in `frontend/src/`
2. Changes hot-reload in dev server
3. Check browser console for errors

### Testing Your Changes

```bash
# Test backend API
python -m pytest backend/tests/ -v

# Test frontend build
npm run build

# Run linting
npm run lint
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/your-feature`)
3. **Make** your changes
4. **Test** thoroughly
5. **Commit** with clear messages (`git commit -m 'Add feature'`)
6. **Push** to your branch
7. **Create** a Pull Request

### Coding Standards
- Follow PEP 8 for Python
- Use Prettier for JavaScript formatting
- Write meaningful commit messages
- Include comments for complex logic

---

## 📄 License

This project is an educational project created by **Paul Kiragu Mburu**.

---


---

## Project Status

| Component | Status |
|-----------|--------|
| Backend API | ✅ Active |
| Frontend UI | ✅ Active |
| ML Models | ✅ Trained & Ready |
| Docker Setup | ✅ Configured |
| Documentation | ✅ Complete |

---

**Last Updated:** April 2026

---

## 🙏 Acknowledgments

- **Open-Meteo** for weather data API
- **OpenStreetMap/Nominatim** for geolocation services
- **Flask, React, TailwindCSS** communities
- Kenyan farmers and agricultural organizations for feedback

---


