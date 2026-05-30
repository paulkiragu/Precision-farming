from flask import Flask, request, jsonify, render_template, make_response
from app.config.settings import Config
import logging
import os

def create_app(config_class=Config):
    # Setup logging first
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure CORS with environment-based origins
    default_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
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
    from app.routes.api_routes import api
    app.register_blueprint(api, url_prefix='/api')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'success': False, 'error': 'Method not allowed'}), 405
    
    logger.info("Flask application initialized successfully")
    return app

# Create app instance for production (Gunicorn)
app = create_app()

if __name__ == '__main__':
    # Use environment variable for debug mode, default to False for production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)