from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS
from app.config.settings import Config
import logging
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure CORS with environment-based origins
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', 
        "http://localhost:5173,http://localhost:3000,https://precision-farming-ihij.onrender.com").split(',')
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
    
    CORS(app,
        origins=allowed_origins,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "Accept"],
        supports_credentials=False,
        max_age=3600
    )

    # Handle preflight OPTIONS requests globally
    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            response = make_response()
            origin = request.headers.get('Origin')
            if origin in allowed_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
            response.headers["Access-Control-Max-Age"] = "3600"
            response.status_code = 204
            return response

    # Add CORS headers to responses
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
        return response

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
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
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Use environment variable for debug mode, default to False for production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)