"""
Main Flask Application
Entry point for the Crop Recommendation API
"""

import os
import logging
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        JSON_SORT_KEYS=False,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max request size
    )
    
    # Configure CORS with environment-based origins
    default_origins = [
        "http://localhost:3000", 
        "http://localhost:5173",
        "http://localhost:5174",
        "http://192.168.100.99:5173",
        "http://192.168.100.99:5174",
        "https://precision-farming-ihij.onrender.com",
        "https://www.precision-farming-ihij.onrender.com"
    ]
    
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', ','.join(default_origins)).split(',')
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
    
    logger.info(f"CORS allowed origins: {allowed_origins}")

    # Handle preflight OPTIONS requests
    @app.before_request
    def handle_cors_preflight():
        if request.method == "OPTIONS":
            headers = {
                'Access-Control-Allow-Origin': request.headers.get('Origin', '*'),
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': request.headers.get('Access-Control-Request-Headers', 'Content-Type, Authorization, Accept'),
                'Access-Control-Max-Age': '86400'
            }
            return '', 200, headers

    # Add CORS headers to all responses
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        
        # Check if origin is allowed
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
            response.headers['Access-Control-Max-Age'] = '86400'
        
        return response
    
    # Register blueprints
    from .routes.api_routes import api
    app.register_blueprint(api, url_prefix='/api')
    
    # Root endpoint
    @app.route('/')
    def index():
        return {
            'name': 'Kenyan Crop Recommendation API',
            'version': '1.0.0',
            'status': 'active',
            'endpoints': {
                'predict': '/api/predict',
                'health': '/api/health',
                'soil_types': '/api/soil-types',
                'crops': '/api/crops'
            },
            'documentation': '/api/docs'
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {'success': False, 'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server error: {e}")
        return {'success': False, 'error': 'Internal server error'}, 500
    
    logger.info("Flask application initialized successfully")
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )