"""
WSGI entry point for production deployment
Used by Gunicorn and other WSGI servers
"""

import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the pre-created app instance
from app import app

if __name__ == '__main__':
    app.run()
