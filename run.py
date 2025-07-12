#!/usr/bin/env python3
"""
Main application entry point for propER system
"""

import os
from app import create_app

# Set default environment
os.environ.setdefault('FLASK_ENV', 'development')

# Create Flask application
app = create_app('development')

if __name__ == '__main__':
    # Get configuration from environment
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting propER system on http://{host}:{port}")
    print(f"📊 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )
