from flask import Blueprint, jsonify, request

from .xai_module.llmshap_service import LLMShapService
from .xai_module.llmshap_config import LLMShapConfig
from .db import get_db


api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/health")
def health_check():
    return jsonify({"status": "ok"})


@api.get("/tasks")
def list_tasks():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT id, title, description, done, created_at, updated_at
            FROM tasks
            ORDER BY id DESC
            """
        )
        rows = cur.fetchall()
    return jsonify(rows)

@api.get("/llmshap/test")
def test_llmshap():
	config = LLMShapConfig(
		system_instruction="Add the word banana to the answer if the question is about France",
		ignored_tokens=[]
	)
	service = LLMShapService(config)
	data = {
		"question1": "What is the capital of France?",
		"question2": "What is the largest mammal?",
	}
	output, attribution = service.compute_diagnosis(data)
	return jsonify({"output": output, "attribution": attribution})

@api.post("/tasks")
def create_task():
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    description = (payload.get("description") or "").strip()

    if not title:
        return jsonify({"error": "title is required"}), 400

    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO tasks (title, description, done)
            VALUES (%s, %s, %s)
            RETURNING id, title, description, done, created_at, updated_at
            """,
            (title, description, False),
        )
        task = cur.fetchone()
    db.commit()

    return jsonify(task), 201


@api.patch("/tasks/<int:task_id>")
def update_task(task_id: int):
    payload = request.get_json(silent=True) or {}
    db = get_db()

    with db.cursor() as cur:
        cur.execute(
            """
            SELECT id, title, description, done, created_at, updated_at
            FROM tasks
            WHERE id = %s
            """,
            (task_id,),
        )
        current = cur.fetchone()

        if current is None:
            return jsonify({"error": "task not found"}), 404

        title = payload.get("title", current["title"])
        description = payload.get("description", current["description"])
        done = payload.get("done", current["done"])

        title = title.strip() if isinstance(title, str) else ""
        description = description.strip() if isinstance(description, str) else ""
        done = bool(done)

        if not title:
            return jsonify({"error": "title is required"}), 400

        cur.execute(
            """
            UPDATE tasks
            SET title = %s, description = %s, done = %s
            WHERE id = %s
            RETURNING id, title, description, done, created_at, updated_at
            """,
            (title, description, done, task_id),
        )
        updated = cur.fetchone()

    db.commit()
    return jsonify(updated)


@api.delete("/tasks/<int:task_id>")
def delete_task(task_id: int):
    db = get_db()
    with db.cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,))
        deleted = cur.fetchone()
    db.commit()

    if deleted is None:
        return jsonify({"error": "task not found"}), 404

    return "", 204
