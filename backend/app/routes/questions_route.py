# questions_routes.py

from flask import Blueprint, request, jsonify
from ..services.questions_service import (
    generate_questions as generate_questions_service,
    save_questions as save_questions_service,
    get_questions as get_questions_service,
    save_answers as save_answers_service,
    get_answers as get_answers_service,
    parse_questions
)

from ..services.projects_service import (
    update_project_prompt
)


bp = Blueprint("questions", __name__)

@bp.route("/questions/generate/<int:project_id>", methods=["POST"])
def generate_questions_route(project_id):
    data = request.get_json()

    text = data.get("text")

    if not text:
        return jsonify({"error": "text is required"}), 400

    try:
        # 1. generate AI output
        result = generate_questions_service(text)

        # 2. parse to structured typed dict
        parsed_questions = parse_questions(result)

        # 3. save questions
        save_questions_service(project_id, parsed_questions)

        # 4. update project prompt
        update_project_prompt(project_id, text)

        return jsonify({
            "questions": parsed_questions
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@bp.route("/questions/<int:project_id>", methods=["POST"])
def save_questions(project_id):
    data = request.get_json()

    questions = data.get("questions")

    if not questions:
        return jsonify({"error": "questions are required"}), 400

    try:
        save_questions_service(project_id, questions)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@bp.route("/questions/<int:project_id>", methods=["GET"])
def get_questions(project_id):
    try:
        questions = get_questions_service(project_id)
        return jsonify(questions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@bp.route("/answers/<int:project_id>", methods=["POST"])
def save_answers(project_id):
    data = request.get_json()

    answers = data.get("answers")

    if not answers:
        return jsonify({"error": "answers are required"}), 400

    try:
        save_answers_service(project_id, answers)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@bp.route("/answers/<int:project_id>", methods=["GET"])
def get_answers(project_id):
    try:
        answers = get_answers_service(project_id)
        return jsonify(answers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
