import os

from flask import Flask
from flask_cors import CORS

from .db import init_app as init_db
from .routes.projects_route import bp as projects_bp


def create_app() -> Flask:
	app = Flask(__name__)
	app.config["DATABASE_URL"] = os.getenv(
		"DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hackathon"
	)

	CORS(app, resources={r"/api/*": {"origins": "*"}})
	init_db(app)
	app.register_blueprint(projects_bp, url_prefix="/api")


	return app
