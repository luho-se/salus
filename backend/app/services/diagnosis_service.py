from typing import cast, Optional, Any, TypedDict
from enum import Enum
import json

from .projects_service import get_project
from .questions_service import get_questions
from .questions_service import get_answers
from .questions_service import Question
from .questions_service import Answer
from ..modules.xai_module.llmshap_service import LLMShapService
from ..modules.xai_module.llmshap_config import LLMShapConfig
from ..db import get_db
from psycopg.rows import dict_row
from psycopg import Connection, Error as PsycopgError
from pathlib import Path

PROMPT_PATH = Path(__file__).parent / "resources" / "ai_prompts" / "d_gen.txt"


def load_prompt():
	return PROMPT_PATH.read_text()

class DiagnosisJobStatus(str, Enum):
	RUNNING = "RUNNING"
	COMPLETED = "FINISHED"
	FAILED = "FAILED"

class DiagnosisItemProbability(str, Enum):
	LOW = "LOW"
	MEDIUM = "MEDIUM"
	HIGH = "HIGH"


class DiagnosisCareType(str, Enum):
	SELF_CARE = "SELF_CARE"
	PROFESSIONAL_CARE = "PROFESSIONAL_CARE"
	EMERGENCY_CARE = "EMERGENCY_CARE"


class Diagnosis(TypedDict):
	id: int
	project_id: int
	created_at: Optional[str]


class DiagnosisItem(TypedDict):
	id: int
	diagnosis_id: int
	title: str
	probability: DiagnosisItemProbability
	care_type: DiagnosisCareType
	motivation: str
	recommendations: str


class DiagnosisSentenceWeight(TypedDict):
	id: int
	diagnosis_id: int
	sentence: str
	weight: float

class DiagnosisReturn(TypedDict):
	id: int
	project_id: int
	created_at: str
	diagnosis_items: list[DiagnosisItem]
	diagnosis_weights: list[DiagnosisSentenceWeight]


def create_diagnosis(project_id: int, diagnosis_id: int) -> None:
	"""
	Creates a new diagnosis for the given project_id and diagnosis_id by executing the LLMShapService
	to compute the diagnosis based on the initial prompt, questions and answers of the project.

	Parameters:
		project_id (int)
		diagnosis_id (int)
	Returns:
		int: The ID of the created diagnosis or None if an error occurs
	"""
	try:

		def construct_q_and_a_item(question: str, answer: str) -> str:
			return f"<Question>{question}</Question><Answer>{answer}</Answer>"

		# Construct the input for the LLMShapService
		project = get_project(project_id)
		if project is None:
			raise ValueError("Project not found")
		
		initial_prompt = project.get("initial_prompt")
		if initial_prompt is None:
			raise ValueError("Initial prompt for project not found")
		
		questions: list[Question] = get_questions(project_id)
		answers: list[Answer] = get_answers(project_id)

		data = {
			"initial_prompt": initial_prompt,
		}

		for q in questions:
			answer = next((a for a in answers if a["question_id"] == q["id"]), None)
			if answer is None:
				raise ValueError(f"No answer found for question ID {q['id']}")
			data[f"q{q['id']}"] = construct_q_and_a_item(q["question"], answer["answer"])

		config = LLMShapConfig(system_instruction=load_prompt())
		llmshap_service = LLMShapService(config=config)
		diagnosis, attribution = llmshap_service.compute_diagnosis(data)

		print("Diagnosis result:", diagnosis)
		print("Attribution:", attribution)

		d_items: list[DiagnosisItem] = parse_diagnosis(diagnosis)
		d_weights: list[DiagnosisSentenceWeight] = parse_attribution(attribution)

		diagnosis_id = save_diagnosis(project_id)
		save_diagnosis_items(diagnosis_id, d_items)
		save_diagnosis_sentence_weights(diagnosis_id, d_weights)
		return
	except Exception as e:
		update_diagnosis_status(diagnosis_id, DiagnosisJobStatus.FAILED.value)
		delete_diagnosis(diagnosis_id)
		return

def create_diagnosis_status(project_id: int, diagnosis_id: int) -> Optional[int]:
	"""
	Creates a new diagnosis status for the given project_id by inserting a new record into the diagnosis_job_status table
	with status set to RUNNING. The actual diagnosis computation will be handled asynchronously by a background worker.

	Parameters:
		project_id (int)
		diagnosis_id (int)
	Returns:
		Optional[int]: The ID of the created diagnosis job or None if an error occurs
	"""
	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			cur.execute(
				"""
				INSERT INTO diagnosis_job_status (project_id, diagnosis_id, job_status)
				VALUES (%s, %s, %s);
				""",
				(project_id, diagnosis_id, DiagnosisJobStatus.RUNNING.value)
			)
			row = cur.fetchone()
		db.commit()
		return cast(int, row["diagnosis_id"]) if row else None
	except PsycopgError as e:
		print(f"Database error: {e}")
		db.rollback()
		return None
	

def update_diagnosis_status(diagnosis_id: int, new_status: DiagnosisJobStatus):
	"""
	Updates status of diagnosis

	Parameters:
		diagnosis_id (int)
		new_status (DiagnosisJobStatus)
	"""
	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			cur.execute(
				"""
				UPDATE diagnosis_job_status 
				SET job_status = %s 
				WHERE diagnosis_id = %s;
				""",
				(new_status.value, diagnosis_id)
			)
		db.commit()
	except PsycopgError as e:
		print(f"Database error: {e}")
		db.rollback()
		return None


def get_diagnosis_status(diagnosis_id: int) -> Optional[DiagnosisJobStatus]:
	"""
	Returns the status of the diagnosis job for the given diagnosis_id

	Parameters:
		diagnosis_id (int)
	Returns:
		DiagnosisJobStatus or None if not found or on error
	"""
	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			cur.execute(
				"""
				SELECT job_status FROM diagnosis_job_status
				WHERE diagnosis_id = %s
				""",
			   (diagnosis_id,)
			)
			row = cur.fetchone()
			return cast(DiagnosisJobStatus, row["status"]) if row else None
	except PsycopgError as e:
		print(f"Database error: {e}")
		return None


def parse_diagnosis(diagnosis: dict) -> list[DiagnosisItem]:
    data = json.loads(diagnosis)
    return [DiagnosisItem(**item) for item in data["diagnosis"]]


def parse_attribution(attribution: dict) -> Optional[list[DiagnosisSentenceWeight]]:
	# Implementation for handling attribution
	pass


def save_diagnosis(project_id: int) -> int:
	"""
	Saves the diagnosis to the database

	Parameters:
		project_id (int)
	Returns:
		int: The ID of the saved diagnosis or None if an error occurs
	"""
	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			cur.execute(
				"""
				INSERT INTO diagnosis (project_id)
				VALUES (%s)
				RETURNING id;
				""",
				(project_id,)
			)
			row = cur.fetchone()  # fetch before commit
		db.commit()
		return cast(int, row["id"]) if row else None
	except PsycopgError as e:
		print(f"Database error: {e}")
		db.rollback()
		return None


def delete_diagnosis(diagnosis_id: int) -> bool:
	"""
	Deletes the diagnosis from the database

	Parameters:
		diagnosis_id (int)
	Returns:
		bool: True if deleted, False if an error occurs
	"""
	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor() as cur:
			cur.execute(
			"""
			DELETE FROM diagnosis WHERE id = %s;
			""",
			(diagnosis_id,)
			)
			db.commit()
			return True
	except PsycopgError as e:
		print(f"Database error: {e}")
		db.rollback()
		return False


def save_diagnosis_items(diagnosis_id: int, items: list[DiagnosisItem]) -> bool:
	"""
	Saves the diagnosis items to the database for the given diagnosis_id

	Parameters:
		diagnosis_id (int)
		items (list[DiagnosisItem])
	Returns:
		bool: True if successful, False otherwise
	"""
	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			for item in items:
				cur.execute(
					"""
					INSERT INTO diagnosis_item (diagnosis_id, title, probability, care_type, motivation, recommendations)
					VALUES (%s, %s, %s, %s, %s, %s);
					""",
					(diagnosis_id, item["title"], item["probability"], item["care_type"], item["motivation"], item["recommendations"])
				)
		db.commit()
		return True
	except PsycopgError as e:
		print(f"Database error: {e}")
		db.rollback()
		return False
	
def save_diagnosis_sentence_weights(diagnosis_id: int, weights: list[DiagnosisSentenceWeight]) -> bool:
	"""
	Saves the diagnosis sentence weights to the database for the given diagnosis_id

	Parameters:
		diagnosis_id (int)
		weights (list[DiagnosisSentenceWeight])
	Returns:
		bool: True if successful, False otherwise
	"""
	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			for weight in weights:
				cur.execute(
					"""
					INSERT INTO diagnosis_sentence_weight (diagnosis_id, sentence, weight)
					VALUES (%s, %s, %s);
					""",
					(diagnosis_id, weight["sentence"], weight["weight"])
				)
		db.commit()
		return True
	except PsycopgError as e:
		print(f"Database error: {e}")
		db.rollback()
		return False

def get_diagnosis(diagnosis_id: int) -> Optional[Diagnosis]:
	"""
	Returns the diagnosis for the given diagnosis_id

	Parameters:
		diagnosis_id (int)
	Returns:
		Diagnosis or None if not found or on error
	"""
	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			cur.execute(
				"""
				SELECT * FROM diagnosis 
				WHERE id = %s;
				""",
			   (diagnosis_id,)
			)
			row = cur.fetchone()
			return cast(Diagnosis, row) if row else None
	except PsycopgError as e:
		print(f"Database error: {e}")
		return None


def get_latest_diagnosis(project_id: int) -> Optional[Diagnosis]:
	"""
	Returns the latest diagnosis for the given project_id

	Parameters:
		project_id (int)
	Returns:
		Diagnosis or None if not found or on error
	"""
	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			cur.execute(
				"""
				SELECT * FROM diagnosis 
				WHERE project_id = %s 
				ORDER BY created_at DESC 
				LIMIT 1;
				""",
			   (project_id,)
			)
			row = cur.fetchone()
			return cast(Diagnosis, row) if row else None
	except PsycopgError as e:
		print(f"Database error: {e}")
		return None


def get_diagnosis_list(project_id: int) -> Optional[list[Diagnosis]]:
	"""
	Returns a list of diagnosis ids for the given project_id,
	ordered by created_at in descending order.

	Parameters:
		project_id (int)
	Returns:
		list[Diagnosis] or None if not found or on error
	"""
	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			cur.execute(
				"""
				SELECT * FROM diagnosis 
				WHERE project_id = %s
				ORDER BY created_at DESC;
				""",
			   (project_id,)
			)
			row = cur.fetchall()
			return cast(list[Diagnosis], [r for r in row]) if row else None
	except PsycopgError as e:
		print(f"Database error: {e}")
		return None


def get_diagnosis_items(diagnosis_id: int) -> Optional[list[DiagnosisItem]]:
	"""
	Returns a list of diagnosis items for the given diagnosis_id
	Parameters:
		diagnosis_id (int)
	Returns:
		list of DiagnosisItem or None if not found or on error
	"""
	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			cur.execute(
				"""
				SELECT * FROM diagnosis_item 
				WHERE diagnosis_id = %s;
				""",
			   (diagnosis_id,)
			)
			rows = cur.fetchall()
			return cast(list[DiagnosisItem], [r for r in rows]) if rows else None
	except PsycopgError as e:
		print(f"Database error: {e}")
		return None


def get_diagnosis_sentence_weights(diagnosis_id: int) -> Optional[list[DiagnosisSentenceWeight]]:
	"""
	Returns a list of diagnosis sentence weights for the given diagnosis_id
	Parameters:
		diagnosis_id (int)
	Returns:
		list of DiagnosisSentenceWeight or None if not found or on error
	"""
	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			cur.execute(
				"""
				SELECT * FROM diagnosis_sentence_weight
				WHERE diagnosis_id = %s;
				""",
			   (diagnosis_id,)
			)
			rows = cur.fetchall()
			return cast(list[DiagnosisSentenceWeight], [r for r in rows]) if rows else None
	except PsycopgError as e:
		print(f"Database error: {e}")
		return None
