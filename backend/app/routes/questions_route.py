# questions_routes.py

from flask import Blueprint, request, jsonify
from ..services.questions_service import (
    generate_questions as generate_questions_service,
    generate_follow_up_questions as generate_follow_up_questions_service,
    save_questions as save_questions_service,
    get_questions as get_questions_service,
    save_answers as save_answers_service,
    get_answers as get_answers_service,
    save_additional_info as save_additional_info_service,
)


bp = Blueprint("questions", __name__)

    
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


@bp.route("/projects/<int:project_id>/additional_info", methods=["POST"])
def save_additional_info(project_id):
    data = request.get_json()
    answer = data.get("answer", "")
    try:
        save_additional_info_service(project_id, answer)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/questions/<int:project_id>/follow_up", methods=["POST"])
def generate_follow_up_questions(project_id):
    try:
        result = generate_follow_up_questions_service(project_id)
        needs_more = result.get("needs_more_questions", False)
        new_questions = []
        if needs_more and result.get("questions"):
            save_questions_service(project_id, result["questions"])
            new_questions = get_questions_service(project_id)
        return jsonify({
            "needs_more_questions": needs_more,
            "questions": new_questions,
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
