from typing import Any, List, Optional, TypedDict, Dict

from openai import OpenAI
import json
from pathlib import Path
from psycopg import Connection, Error as PsycopgError
from ..db import get_db
from psycopg.rows import dict_row





client = OpenAI()

PROMPT_PATH = Path(__file__).parent / "resources" / "ai_prompts"

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
    llm_generated: bool
    created_at: str
    updated_at: str

def load_prompt(filename: str) -> str:
	return (PROMPT_PATH / filename).read_text()


def generate_questions(text: str) -> Dict[str, Any]:

	system_prompt = load_prompt("q_gen.txt")
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
	

def generate_follow_up_questions(project_id: int) -> Dict[str, Any]:
	system_prompt = load_prompt("fu_q_gen.txt")
	questions = get_questions(project_id)
	answers = get_answers(project_id)

	# create input text by pairing questions and answers with format json
	answer_map = {a["question_id"]: a["answer"] for a in answers}
	pairs = [
		{
			"question": q["question"],
			"answer": answer_map.get(q["id"])
		}
		for q in questions
		if answer_map.get(q["id"]) is not None
	]

	if not pairs:
		raise ValueError("No answered questions available")

	input_text = json.dumps(pairs)

	response = client.chat.completions.create(
		model="gpt-4o-mini",
		messages=[
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": input_text}
		],
		temperature=0.3,
		response_format={"type": "json_object"}
	)

	content = response.choices[0].message.content

	try:
		return json.loads(content)
	except json.JSONDecodeError:
		raise ValueError("Invalid JSON from AI")


def save_questions(project_id: int, questions: List[Question]) -> List[int]:
	"""
	Insert a list of questions into the database.

	Returns:
		List of inserted question IDs in the same order as input.
	"""
	if not questions:
		return []

	try:
		db: Connection[dict[str, Any]] = get_db()
		ids: List[int] = []
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
					VALUES (%s, %s, %s, %s, %s, %s)
					RETURNING id;
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
				row = cur.fetchone()
				ids.append(row["id"])

		db.commit()
		return ids

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
				input_max,
				created_at
			FROM questions
			WHERE project_id = %s
			ORDER BY id ASC;
			""",
			(project_id,)
		)

		rows = cur.fetchall()

	return [dict(row) for row in rows]

def save_answers(project_id: int, answers: list[dict]) -> bool:
	"""
	Insert or update multiple answers for a project.
	Each dict may include 'llm_generated' (bool, default False).

	Returns:
		True if successful, raises Exception otherwise.
	"""

	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			for a in answers:
				question_id = a.get("question_id")
				answer = a.get("answer")
				llm_generated = bool(a.get("llm_generated", False))

				if question_id is None:
					raise ValueError("Missing question_id in answers payload")

				cur.execute(
					"""
					INSERT INTO answers (
						project_id,
						question_id,
						answer,
						llm_generated
					)
					VALUES (%s, %s, %s, %s)
					ON CONFLICT (project_id, question_id)
					DO UPDATE SET
						answer = EXCLUDED.answer,
						llm_generated = EXCLUDED.llm_generated,
						updated_at = CURRENT_TIMESTAMP;
					""",
					(project_id, question_id, answer, llm_generated)
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
				llm_generated,
				created_at,
				updated_at
			FROM answers
			WHERE project_id = %s
			ORDER BY id DESC;
			""",
			(project_id,)
		)

		rows = cur.fetchall()

	return [dict(row) for row in rows]




def save_additional_info(project_id: int, answer: str) -> None:
	"""
	Upserts an 'Additional information' question for the project (if it doesn't exist)
	and saves/updates its answer.
	"""
	db: Connection[dict[str, Any]] = get_db()
	with db.cursor(row_factory=dict_row) as cur:
		cur.execute(
			"""
			SELECT id FROM questions
			WHERE project_id = %s AND question = 'Additional information'
			LIMIT 1;
			""",
			(project_id,)
		)
		row = cur.fetchone()
		if row:
			question_id = row["id"]
		else:
			cur.execute(
				"""
				INSERT INTO questions (project_id, question, input_type)
				VALUES (%s, 'Additional information', 'text')
				RETURNING id;
				""",
				(project_id,)
			)
			question_id = cur.fetchone()["id"]

		cur.execute(
			"""
			INSERT INTO answers (project_id, question_id, answer)
			VALUES (%s, %s, %s)
			ON CONFLICT (project_id, question_id)
			DO UPDATE SET answer = EXCLUDED.answer, updated_at = CURRENT_TIMESTAMP;
			""",
			(project_id, question_id, answer)
		)
	db.commit()


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
