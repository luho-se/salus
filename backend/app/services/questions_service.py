from typing import Any, List, Optional, TypedDict

from openai import OpenAI
import json
from pathlib import Path
from psycopg import Connection, Error as PsycopgError
from ..db import get_db
from psycopg.rows import dict_row




client = OpenAI()

PROMPT_PATH = Path(__file__).parent / "resources" / "ai_prompts" / "q_gen.txt"

class Question(TypedDict):
    id: int
    project_id: int
    question: str
    input_type: str
    input_unit: Optional[str]
    input_min: Optional[float]
    input_max: Optional[float]

class Answer(TypedDict):
    id: int
    project_id: int
    question_id: int
    answer: Optional[str]
    created_at: str
    updated_at: str

def load_prompt():
	return PROMPT_PATH.read_text()


def generate_questions(text: str):

	system_prompt = load_prompt()
	user_input = f"""Description: {text}"""

	response = client.chat.completions.create(
		model="gpt-4o-mini",
		messages=[
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": user_input}
		],
		temperature=0.3,
		response_format={"type": "json_object"}
	)

	content = response.choices[0].message.content

	try:
		return json.loads(content)
	except json.JSONDecodeError:
		raise ValueError("Invalid JSON from AI")
	


def save_questions(project_id: int, questions: List[Question]) -> bool:
	"""
	Insert a list of questions into the database.

	Returns:
		True if successful, raises Exception otherwise.
	"""
	if not questions:
		return True 

	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			for q in questions:
				question = q.get("question")
				input_type = q.get("input_type")

				if not question or not input_type:
					raise ValueError("Missing required fields in question")

				input_unit = q.get("input_unit")
				input_min = q.get("input_min")
				input_max = q.get("input_max")

				cur.execute(
					"""
					INSERT INTO questions (
						project_id,
						question,
						input_type,
						input_unit,
						input_min,
						input_max
					)
					VALUES (%s, %s, %s, %s, %s, %s);
					""",
					(
						project_id,
						question,
						input_type,
						input_unit,
						input_min,
						input_max
					)
				)

		db.commit()
		return True

	except Exception:
		db.rollback()
		raise

def get_questions(project_id: int) -> List[Question]:
	"""
	Retrive a list of questions from the database.
	"""
	db: Connection[dict[str, Any]] = get_db()
	with db.cursor(row_factory=dict_row) as cur:
		cur.execute(
			"""
			SELECT
				id,
				project_id,
				question,
				input_type,
				input_unit,
				input_min,
				input_max
			FROM questions
			WHERE project_id = %s
			ORDER BY id DESC;
			""",
			(project_id,)
		)

		rows = cur.fetchall()

	questions: List[Question] = []

	for row in rows:
		q: Question = {
			"id": row[0],
			"project_id": row[1],
			"question": row[2],
			"input_type": row[3],
			"input_unit": row[4],
			"input_min": row[5],
			"input_max": row[6],
		}

		questions.append(q)

	return questions

def save_answers(project_id: int, answers: list[dict]) -> bool:
	"""
	Insert or update multiple answers for a project.

	Returns:
		True if successful, raises Exception otherwise.
	"""

	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			for a in answers:
				question_id = a.get("question_id")
				answer = a.get("answer")

				if question_id is None:
					raise ValueError("Missing question_id in answers payload")

				cur.execute(
					"""
					INSERT INTO answers (
						project_id,
						question_id,
						answer
					)
					VALUES (%s, %s, %s)
					ON CONFLICT (project_id, question_id)
					DO UPDATE SET
						answer = EXCLUDED.answer,
						updated_at = CURRENT_TIMESTAMP;
					""",
					(project_id, question_id, answer)
				)

		db.commit()
		return True

	except Exception:
		db.rollback()
		raise


def get_answers(project_id: int) -> List[Answer]:
	"""
	Retrieve all answers for a project.
	"""

	db: Connection[dict[str, Any]] = get_db()
	with db.cursor(row_factory=dict_row) as cur:
		cur.execute(
			"""
			SELECT
				id,
				project_id,
				question_id,
				answer,
				created_at,
				updated_at
			FROM answers
			WHERE project_id = %s
			ORDER BY id DESC;
			""",
			(project_id,)
		)

		rows = cur.fetchall()

	answers: List[Answer] = []

	for row in rows:
		answers.append({
			"id": row[0],
			"project_id": row[1],
			"question_id": row[2],
			"answer": row[3],
			"created_at": row[4],
			"updated_at": row[5],
		})
	return answers




def parse_questions(data) -> List[Question]:
    questions = data.get("questions", [])

    parsed: List[Question] = []

    for q in questions:
        parsed.append({
            "id": q.get("id", 0),
            "project_id": q.get("project_id", 0),
            "question": q["question"],
            "input_type": q["input_type"],
            "input_unit": q.get("input_unit"),
            "input_min": q.get("input_min"),
            "input_max": q.get("input_max"),
        })

    return parsed
