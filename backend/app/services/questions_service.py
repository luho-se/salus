from openai import OpenAI
import json
from pathlib import Path

client = OpenAI()

PROMPT_PATH = Path(__file__).parent / "resources" / "ai_prompts" / "q_gen.txt"

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