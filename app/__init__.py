from flask import Flask
from app.routes.voice_assistant import bp as voice_assistant_bp
from app.config.config import Config


def create_app():
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(voice_assistant_bp)

    return app
