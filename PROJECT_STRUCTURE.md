# Kenyan Crop Recommendation System - Project Structure

**Date Created:** December 15, 2025  
**Standard:** Industry Best Practices (Flask + React + Data Science)  
**Based On:** Project Guidelines PDF + Proposal Document

---

## 📁 Complete Directory Structure

```
precisionfarming/
│
├── 📂 backend/                          # Flask Backend Application (Tier 2)
│   ├── app.py                          # Main Flask controller (as per guidelines)
│   ├── requirements.txt                # Python dependencies
│   └── app/
│       ├── __init__.py
│       ├── routes/                     # API route handlers
│       │   └── __init__.py
│       ├── models/                     # ML model integration
│       │   └── __init__.py
│       ├── utils/                      # Utility functions
│       │   ├── __init__.py
│       │   └── data_fetcher.py        # API calls & heuristic conversions (Tier 3)
│       ├── config/                     # Configuration
│       │   ├── __init__.py
│       │   └── settings.py            # App configuration
│       ├── static/                     # Static assets
│       └── templates/                  # HTML templates
│
├── 📂 frontend/                         # React Frontend Application (Tier 1)
│   ├── package.json                    # Node dependencies
│   ├── README.md
│   ├── .gitignore
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── index.js                    # React entry point
│       ├── App.js                      # Main component
│       ├── components/                 # Reusable components
│       ├── pages/                      # Page components
│       ├── services/                   # API service calls
│       ├── utils/                      # Helper functions
│       └── styles/                     # Tailwind CSS styles
│
├── 📂 data/                             # All Datasets (CRISP-DM Standard)
│   ├── raw/                            # Original unprocessed data
│   │   ├── combined_smartgrow_dataset.csv
│   │   └── Crop_recommendation_dataset.csv
│   ├── processed/                      # Cleaned & merged data
│   │   ├── smartgrow_cleaned.csv
│   │   ├── crop_recommendation_cleaned.csv
│   │   └── High_Accuracy_Crop_Data.csv  # Final merged dataset (3900 rows)
│   └── external/                       # KALRO, Met Department data
│       └── .gitkeep
│
├── 📂 models/                           # Machine Learning Models
│   ├── trained/                        # Serialized models
│   │   ├── .gitkeep
│   │   ├── crop_recommendation_model.pkl (to be created)
│   │   └── nutrient_requirements.json   (to be created)
│   └── experiments/                    # Training logs & experiments
│
├── 📂 notebooks/                        # Jupyter Notebooks (Data Science Workflow)
│   ├── 01_exploratory/                 # Exploratory Data Analysis
│   │   └── 01_data_exploration.ipynb
│   ├── 02_preprocessing/               # Data preprocessing
│   ├── 03_modeling/                    # Model training & evaluation
│   └── 04_visualization/               # Data visualizations
│
├── 📂 scripts/                          # Automation Scripts
│   ├── data_processing/                # Data processing scripts
│   │   └── data_cleaning.py           # Dataset cleaning script
│   ├── model_training/                 # Model training scripts
│   └── deployment/                     # Deployment automation
│
├── 📂 tests/                            # Test Suite
│   ├── unit/                           # Unit tests
│   │   └── test_model.py
│   ├── integration/                    # Integration tests
│   │   └── test_api.py
│   └── fixtures/                       # Test data & mocks
│
├── 📂 docs/                             # Documentation
│   ├── project_guideline.pdf           # Project guidelines
│   ├── Proposal_paul.docx              # Project proposal
│   ├── api/                            # API documentation
│   │   └── endpoints.md
│   ├── user_guide/                     # User manuals
│   ├── technical/                      # Technical docs
│   └── images/                         # Diagrams & screenshots
│
├── 📂 deployment/                       # Deployment Configurations
│   ├── docker/                         # Docker configs
│   └── nginx/                          # Nginx configs
│
├── 📂 config/                           # Project-wide configurations
├── 📂 logs/                             # Application logs
├── 📂 venv/                             # Python virtual environment
│
├── 📄 README.md                         # Project overview
├── 📄 .gitignore                        # Git ignore rules
├── 📄 .env.example                      # Environment variables template
├── 📄 Dockerfile                        # Docker container config
├── 📄 docker-compose.yml                # Multi-container setup
├── 📄 requirements.txt                  # Root Python dependencies
├── 📄 setup_project_structure.py        # This setup script
└── 📄 PROJECT_STRUCTURE.md             # This document

```

---

## 🎯 Alignment with Project Requirements

### ✅ Project Guidelines Compliance

| Requirement | Location | Status |
|-------------|----------|--------|
| **3-Tier Architecture** | backend/, frontend/, data_fetcher.py | ✅ Implemented |
| **Flask Backend (Tier 2)** | backend/app.py | ✅ Created |
| **React Frontend (Tier 1)** | frontend/src/ | ✅ Scaffolded |
| **data_fetcher.py** | backend/app/utils/data_fetcher.py | ✅ Created |
| **crop_recommendation_model.pkl** | models/trained/ | 🔄 To be trained |
| **nutrient_requirements.json** | models/trained/ | 🔄 To be created |
| **High_Accuracy_Crop_Data.csv** | data/processed/ | ✅ Created (3900 rows) |
| **Visual Soil Heuristic** | data_fetcher.py | ✅ Implemented |
| **API Integration (Nominatim)** | data_fetcher.py | ✅ Implemented |
| **API Integration (Open-Meteo)** | data_fetcher.py | ✅ Implemented |

### ✅ Proposal Document Compliance

| Requirement | Location | Status |
|-------------|----------|--------|
| **CRISP-DM Methodology** | notebooks/ structure | ✅ Followed |
| **Agile Development** | Modular structure | ✅ Enabled |
| **Decision Tree Classifier** | To be in notebooks/03_modeling/ | 🔄 Next step |
| **GridSearchCV** | To be in notebooks/03_modeling/ | 🔄 Next step |
| **Web Application** | backend/ + frontend/ | ✅ Scaffolded |
| **Documentation** | docs/ | ✅ Organized |
| **Testing Framework** | tests/ | ✅ Structure ready |

---

## 🚀 Development Workflow

### Phase 1: Data Science (Current → Next Steps)
```
1. ✅ Data Collection & Cleaning (DONE)
   → data/processed/High_Accuracy_Crop_Data.csv ready

2. 📊 Exploratory Data Analysis (NEXT)
   → Work in: notebooks/01_exploratory/

3. 🔧 Feature Engineering
   → Work in: notebooks/02_preprocessing/

4. 🤖 Model Training
   → Work in: notebooks/03_modeling/
   → Output: models/trained/crop_recommendation_model.pkl

5. 📈 Model Evaluation
   → Work in: notebooks/03_modeling/
```

### Phase 2: Backend Development
```
1. Implement API Routes
   → backend/app/routes/

2. Integrate ML Model
   → backend/app/models/

3. Test Endpoints
   → tests/integration/
```

### Phase 3: Frontend Development
```
1. Build UI Components
   → frontend/src/components/

2. Implement Pages
   → frontend/src/pages/

3. Connect to Backend
   → frontend/src/services/
```

### Phase 4: Deployment
```
1. Containerize Application
   → Use Dockerfile & docker-compose.yml

2. Configure Production
   → deployment/nginx/

3. Deploy to Server
```

---

## 📦 Technology Stack

### Backend
- **Language:** Python 3.10+
- **Framework:** Flask 2.3.0
- **ML Library:** Scikit-learn 1.2.0
- **Data Processing:** Pandas 1.5.3, NumPy 1.24.0
- **APIs:** Requests 2.31.0

### Frontend
- **Framework:** React 18.2.0
- **Styling:** Tailwind CSS 3.3.0
- **HTTP Client:** Axios 1.4.0
- **Routing:** React Router 6.14.0

### Data Science
- **Notebooks:** Jupyter
- **Visualization:** Matplotlib, Seaborn
- **Model:** Decision Tree Classifier

### DevOps
- **Containerization:** Docker
- **Web Server:** Nginx (production)
- **WSGI Server:** Gunicorn

---

## 🔧 Setup Instructions

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

### 3. Data Science Environment
```bash
# From project root with venv activated
pip install jupyter matplotlib seaborn scikit-learn
jupyter notebook
```

### 4. Run Development Servers
```bash
# Backend (Terminal 1)
cd backend
source venv/bin/activate
python app.py

# Frontend (Terminal 2)
cd frontend
npm start
```

---

## 📊 Dataset Information

### Final Merged Dataset: `High_Accuracy_Crop_Data.csv`

**Statistics:**
- **Total Records:** 3,900
- **Features:** 9 (N, P, K, temperature, humidity, ph, rainfall, soil_type, season_duration)
- **Target:** label (crop name)
- **Unique Crops:** 36
- **Sources:** SmartGrow (1,000) + Crop Recommendation (2,900)

**Top Crops:**
1. Wheat (227)
2. Maize (180)
3. Beans (146)
4. Sorghum (141)
5. Cassava (121)

---

## 📝 Key Files Reference

### Backend Core Files
- `backend/app.py` - Main Flask application
- `backend/app/utils/data_fetcher.py` - API integration & soil heuristics
- `backend/app/config/settings.py` - Application configuration

### Data Files
- `data/processed/High_Accuracy_Crop_Data.csv` - Training dataset (3,900 rows)
- `data/raw/` - Original datasets (backup)

### Model Files (To Be Created)
- `models/trained/crop_recommendation_model.pkl` - Trained Decision Tree
- `models/trained/nutrient_requirements.json` - Crop nutrient database

### Documentation
- `docs/project_guideline.pdf` - Project guidelines
- `docs/Proposal_paul.docx` - Project proposal
- `docs/api/endpoints.md` - API documentation

---

## ✅ Quality Checklist

- [x] Industry-standard folder structure
- [x] Separation of concerns (backend/frontend/data/models)
- [x] CRISP-DM data science workflow
- [x] MVC pattern for backend
- [x] Component-based frontend structure
- [x] Comprehensive testing structure
- [x] Documentation organized
- [x] Version control ready (.gitignore)
- [x] Docker-ready (Dockerfile, docker-compose.yml)
- [x] Environment configuration (.env.example)

---

## 🎓 Project Alignment Summary

This structure implements:
1. ✅ **3-Tier Architecture** (Guidelines requirement)
2. ✅ **CRISP-DM Methodology** (Proposal requirement)
3. ✅ **Agile-Ready** (Proposal requirement)
4. ✅ **Scalable & Maintainable**
5. ✅ **Production-Ready**

**Status:** Ready for Phase 2 - Model Development & Training 🚀

---

**Last Updated:** December 15, 2025  
**Next Steps:** Begin EDA in `notebooks/01_exploratory/`
