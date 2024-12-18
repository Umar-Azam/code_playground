import os
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['RECORDINGS_FOLDER'] = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'recordings', 
        'input_logs'
    )
    
    # Ensure recording directory exists
    os.makedirs(app.config['RECORDINGS_FOLDER'], exist_ok=True)
    
    # Register routes
    from app.routes import main
    app.register_blueprint(main)
    
    return app