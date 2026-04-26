from flask import Blueprint, jsonify, request, Response
from typing import Union, Tuple
from ..services.projects_service import (
    list_projects as list_projects_service,
    get_project as get_project_service,
    create_project as create_project_service,
    update_project_prompt
)

from ..services.questions_service import (
    generate_questions as generate_questions_service,
    generate_follow_up_questions as generate_follow_up_question_service,
    save_questions as save_questions_service,
    save_answers as save_answers_service,
    get_questions as get_questions_service,
    parse_questions,
)

bp = Blueprint("projects", __name__)


@bp.route("/projects", methods=["GET"])
def list_projects() -> Response:
    """List all projects."""
    projects = list_projects_service()
    return jsonify(projects)


@bp.route("/projects/<int:project_id>", methods=["GET"])
def get_project(project_id: int) -> Union[Response, Tuple[Response, int]]:
    """Get a project by ID."""
    project = get_project_service(project_id)
    if project is None:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(project)


@bp.route("/projects", methods=["POST"])
def create_project() -> Union[Response, Tuple[Response, int]]:
    """Create a new project."""
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    if not isinstance(data["title"], str) or not data["title"].strip():
        return jsonify({"error": "Title must be a non-empty string"}), 400

    initial_prompt = data.get("initial_prompt", "")
    if not isinstance(initial_prompt, str):
        return jsonify({"error": "initial_prompt must be a string"}), 400

    project = create_project_service(
        title=data["title"],
        initial_prompt=initial_prompt,
    )
    if project is None:
        return jsonify({"error": "Failed to create project"}), 500

    return jsonify(project), 201

@bp.route("/projects/<int:project_id>/generate_questions", methods=["POST"])
def generate_questions(project_id):
    data = request.get_json()

    text = data.get("text")

    if not text:
        return jsonify({"error": "text is required"}), 400

    project = get_project_service(project_id)
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    try:
        result = generate_questions_service(text)

        # Save extracted Q&A pairs (answers pre-filled by AI from the initial prompt)
        extracted = result.get("extracted", [])
        if extracted:
            extracted_questions = [
                {
                    "question": e["question"],
                    "input_type": e["input_type"],
                    "input_unit": e.get("input_unit"),
                    "input_min": e.get("input_min"),
                    "input_max": e.get("input_max"),
                }
                for e in extracted
            ]
            extracted_ids = save_questions_service(project_id, extracted_questions)
            llm_answers = [
                {"question_id": qid, "answer": e["answer"], "llm_generated": True}
                for qid, e in zip(extracted_ids, extracted)
            ]
            save_answers_service(project_id, llm_answers)

        # Save follow-up questions (no pre-filled answers)
        parsed_questions = parse_questions(result)
        save_questions_service(project_id, parsed_questions)

        update_project_prompt(project_id, text)

        db_questions = get_questions_service(project_id)
        return jsonify({"questions": db_questions}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
