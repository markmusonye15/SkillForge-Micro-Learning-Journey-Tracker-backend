import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate 
from datetime import timedelta
from flask_cors import CORS

# --- This print statement will run as soon as the file is imported ---
print("--- Loading server/app.py ---")

# Importing the configuration and database instances
from .config import config
from .models import db, bcrypt, TokenBlocklist 

# Importing the controller Blueprints
from .controllers.auth_controller import auth_bp
from .controllers.journey_controller import journey_bp
from .controllers.step_controller import step_bp

def create_app(config_name=None):
    """
    Application Factory Pattern:
    Creates and configures the Flask application.
    """
    # --- This print statement tells us the factory is running ---
    print("--- create_app() function called ---")

    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    CORS(app, origins=["https://skill-forge-self.vercel.app"])

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
        return token is not None
    
    # --- These print statements will confirm if the routes are being registered ---
    print("--- Registering Blueprints... ---")
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    print("--- Registered auth_bp at /api/auth ---")
    app.register_blueprint(journey_bp, url_prefix='/api/journeys')
    print("--- Registered journey_bp at /api/journeys ---")
    app.register_blueprint(step_bp, url_prefix='/api/steps')
    print("--- Registered step_bp at /api/steps ---")
    
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to the SkillForge API!"})
        
    print("--- create_app() function finished ---")
    return app

# --- This print statement runs when the app instance is created ---
print("--- Creating final app instance ---")
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)



