import os
from flask import Flask
from .models import db
from config import config_options

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_options[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Register Blueprints
    from .routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
