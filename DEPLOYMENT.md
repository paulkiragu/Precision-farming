# Production Deployment Guide

## Environment Variables Required on Render

### Backend Service (precisionfarming-287u on Render)

Set these environment variables in Render dashboard > Settings > Environment:

```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<generate-a-random-secret-key>
PORT=5000
ALLOWED_ORIGINS=https://precision-farming-ihij.onrender.com,https://www.precision-farming-ihij.onrender.com,http://localhost:5173,http://localhost:3000
```

### Frontend Service (precision-farming-ihij on Render)

Set these environment variables in Render dashboard > Settings > Environment:

```
VITE_API_URL=https://precisionfarming-287u.onrender.com
```

## Build and Start Commands

### Backend Service
- **Build Command:** `pip install -r backend/requirements.txt`
- **Start Command:** `gunicorn wsgi:app --bind 0.0.0.0:$PORT`

### Frontend Service
- **Build Command:** `cd frontend && npm install && npm run build`
- **Start Command:** Render automatically serves the dist folder

## CORS Configuration

The backend uses **manual CORS headers** (no Flask-CORS dependency) configured to accept requests from:
- Frontend production URL (https://precision-farming-ihij.onrender.com)  
- Frontend www URL (https://www.precision-farming-ihij.onrender.com)
- Local development URLs (http://localhost:5173, http://localhost:3000)
- Any additional URLs specified in ALLOWED_ORIGINS environment variable

**Important:** All preflight OPTIONS requests return HTTP 200 with proper Access-Control headers.

### How It Works
1. Every `OPTIONS` request gets intercepted and returns 200 immediately
2. The `Access-Control-*` headers are added via `after_request` hook
3. Origins are validated against `ALLOWED_ORIGINS` environment variable

## Troubleshooting

### CORS Preflight Failing
If you see "Access to XMLHttpRequest...has been blocked by CORS policy":

1. Verify ALLOWED_ORIGINS environment variable includes your frontend URL exactly
2. Restart the backend service after changing environment variables
3. Check that both services are using HTTPS in production
4. Verify the frontend is using the correct backend URL (VITE_API_URL environment variable)

### Backend Not Starting
If backend fails to deploy:
1. Check the build log for missing dependencies
2. Verify wsgi.py can be imported: `gunicorn wsgi:app`
3. Check environment variables are properly set
4. Review logs for any initialization errors

## Local Testing

```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
python app.py

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL=http://localhost:5000` in frontend `.env.development`

## Production Checklist

- [ ] Backend environment variables set on Render
- [ ] Frontend environment variables set on Render
- [ ] ALLOWED_ORIGINS includes frontend URL
- [ ] Backend start command uses `gunicorn wsgi:app`
- [ ] Frontend build command runs from correct directory
- [ ] Both services restarted after env var changes
- [ ] Test /api/health endpoint returns 200
- [ ] Test /api/predict with sample data
