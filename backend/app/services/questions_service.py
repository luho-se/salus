from typing import List, Optional, TypedDict

from openai import OpenAI
import json
from pathlib import Path

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

def load_prompt():
	return PROMPT_PATH.read_text()


def generate_questions(text, categories=None):
	categories = categories or []

	system_prompt = load_prompt()
	user_input = f"""Description:
{text}

Symptom Categories:
{", ".join(categories) if categories else "None"}"""

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
	

def save_questions(project_id, questions, conn):
	"""
	Save a list of questions to the database.
	"""

	if not questions:
		return []

	inserted = []

	with conn.cursor() as cur:
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

			inserted_id = cur.fetchone()[0]

			inserted.append({
				"id": inserted_id,
				"question": question
			})

	conn.commit()

	return inserted

def get_questions(project_id: int, conn) -> List[Question]:
	"""
	Retrive a list of questions from the database.
	"""
	with conn.cursor() as cur:
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