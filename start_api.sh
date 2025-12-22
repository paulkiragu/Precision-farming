#!/bin/bash
# Start the Flask API server

echo "🌾 Starting Kenyan Crop Recommendation API..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if venv is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Set Flask environment variables
export FLASK_APP=backend/app
export FLASK_ENV=development

# Start server
echo "🚀 Starting Flask server on http://localhost:5000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Available endpoints:"
echo "   POST /api/predict      - Get crop recommendations"
echo "   GET  /api/health       - Health check + cache stats"
echo "   GET  /api/soil-types   - List supported soil types"
echo "   GET  /api/crops        - List predictable crops"
echo "   POST /api/cache/clear  - Clear cache"
echo ""
echo "💡 Press Ctrl+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python -m backend.app
