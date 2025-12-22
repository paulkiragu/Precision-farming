"""
Main Flask Application
Entry point for the Crop Recommendation API
"""

import os
import logging
from flask import Flask
from flask_cors import CORS

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
    
    # Enable CORS for frontend communication (including mobile access)
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000", 
                "http://localhost:5173",
                "http://localhost:5174",
                "http://192.168.100.99:5173",
                "http://192.168.100.99:5174",
                "*"  # Allow all origins for development
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Register blueprints
    from .routes.api_routes import api
    app.register_blueprint(api)
    
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