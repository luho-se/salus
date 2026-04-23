import os

from flask import Flask
from flask_cors import CORS

from .db import init_app as init_db
from .routes import api


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DATABASE_URL"] = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hackathon"
    )

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    init_db(app)
    app.register_blueprint(api)

    return app
