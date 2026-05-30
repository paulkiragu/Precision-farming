# CORS Fix - Quick Reference

## Problem
```
Access to XMLHttpRequest at 'https://precisionfarming-287u.onrender.com/api/predict' 
from origin 'https://precision-farming-ihij.onrender.com' has been blocked by CORS policy
```

## Root Cause
- Flask-CORS was conflicting with manual CORS handlers
- OPTIONS preflight requests weren't returning proper 200 status with CORS headers

## Solution Implemented

1. **Removed Flask-CORS dependency** - Using manual CORS headers only
2. **Simplified CORS handling** - Clean before_request and after_request hooks
3. **Proper OPTIONS handling** - Returns 200 immediately with all CORS headers

## Files Changed

- `backend/app.py` - Removed Flask-CORS, implemented manual CORS
- `backend/requirements.txt` - Removed flask-cors dependency

## What to Do on Render

### 1. Push code changes
```bash
git add -A
git commit -m "Fix: Implement manual CORS handling without Flask-CORS"
git push origin main
```

### 2. Set Backend Environment Variable

In Render Dashboard > Backend Service Settings > Environment tab:

```
ALLOWED_ORIGINS=https://precision-farming-ihij.onrender.com,https://www.precision-farming-ihij.onrender.com,http://localhost:5173,http://localhost:3000
```

**Important:** Make sure there are NO spaces and URLs are separated by commas.

### 3. Set Frontend Environment Variable  

In Render Dashboard > Frontend Service Settings > Environment tab:

```
VITE_API_URL=https://precisionfarming-287u.onrender.com
```

### 4. Update Backend Start Command

In Render Dashboard > Backend Service Settings > Build & Deploy tab:

- **Start Command:** `gunicorn wsgi:app --bind 0.0.0.0:$PORT`

### 5. Redeploy Both Services

1. Go to Backend Service > Manual Deploy > select your branch
2. Go to Frontend Service > Manual Deploy > select your branch
3. Wait for both to finish deploying
4. Test by visiting the frontend and trying to make a prediction

## Testing Locally

```bash
# Start backend
cd ~/precisionfarming
source .venv/bin/activate
python wsgi.py

# In another terminal, test CORS
bash test-cors.sh
```

## Verify It Works

After deployment, check:

1. **Health check returns 200:**
   ```
   curl https://precisionfarming-287u.onrender.com/api/health
   ```

2. **Browser can make requests** - Try making a prediction in the frontend
3. **No CORS errors in console** - Open DevTools and check Network tab

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Still getting CORS error | Check ALLOWED_ORIGINS env var matches your frontend URL exactly |
| Backend won't start | Run locally with `python wsgi.py` to see error messages |
| Frontend uses wrong API URL | Verify VITE_API_URL environment variable is set and matches backend URL |
| Changes not taking effect | Restart the service after changing environment variables |
