from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask import Flask
from flask_cors import CORS
from app.routes.event_routes import event_bp




# Initialize extensions
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    CORS(app)
    bcrypt.init_app(app)

    # JWT secret
    app.config['JWT_SECRET_KEY'] = 'change-this-secret-key'

    # Initialize JWT
    jwt = JWTManager(app)

    # Import blueprints AFTER initializing JWT
    from app.routes.user_routes import user_bp
    from app.routes.event_routes import event_bp

    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(event_bp, url_prefix='/api/event')

    print("Flask app is starting...")
    return app
