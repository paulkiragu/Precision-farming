"""
Main Flask Application
Manages routes and connects frontend to AI model
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from app.config.settings import Config
import logging

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for React frontend
    CORS(app)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Register blueprints
    from app.routes.api_routes import api
    app.register_blueprint(api, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
