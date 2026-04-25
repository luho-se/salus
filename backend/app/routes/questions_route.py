# questions_routes.py

from flask import Blueprint, request, jsonify
from .questions_services import generate_questions

bp = Blueprint("questions", __name__)

@bp.route("/get_questions", methods=["POST"])
def get_questions():
    """Generate questions based on an initial prompt."""

    data = request.get_json()

    text = data.get("text")
    categories = data.get("categories", [])

    if not text:
        return jsonify({"error": "Missing an initial prompt"}), 400

    result = generate_questions(text, categories)

    return jsonify(result), 200