"""This script initializes and runs the Flask application."""

import os

from app import create_app

# Set FLASK_DEBUG environment variable for debug
debug_mode = os.getenv("FLASK_DEBUG", "false").lower() in ["true", "1", "yes"]
app = create_app(debug=debug_mode)

if __name__ == '__main__':
    app.run(debug=debug_mode)
