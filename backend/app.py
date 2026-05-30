from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS
from app.config.settings import Config
import logging

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    CORS(app,
        origins=["https://precision-farming-ihij.onrender.com"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "Accept"],
        supports_credentials=False
    )

    # Handle preflight OPTIONS requests globally
    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers["Access-Control-Allow-Origin"] = "https://precision-farming-ihij.onrender.com"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
            response.status_code = 200
            return response

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Register blueprints
    from app.routes.api_routes import api
    app.register_blueprint(api, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)