from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from .database import get_connection  # note the dot (.) for relative import

bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    CORS(app)
    bcrypt.init_app(app)

    # Import routes after app is created
    from .routes import register_routes
    register_routes(app)

    return app
