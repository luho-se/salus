from typing import cast, Optional, Any, TypedDict
from enum import Enum

from backend.app.services.projects_service import Project
from backend.app.services.projects_service import ProjectStep
from backend.app.services.questions_service import get_questions
from backend.app.services.questions_service import get_answers
from backend.app.services.questions_service import Question
from backend.app.services.questions_service import Answer
from backend.app.modules.xai_module.llmshap_service import LLMShapService
from backend.app.modules.xai_module.llmshap_config import LLMShapConfig
from ..db import get_db
from psycopg.rows import dict_row
from psycopg import Connection, Error as PsycopgError
from pathlib import Path

from backend.app import db

PROMPT_PATH = Path(__file__).parent / "resources" / "ai_prompts" / "d_gen.txt"


def load_prompt():
	return PROMPT_PATH.read_text()


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


def create_diagnosis(project_id: int) -> int:
	"""
	Creates a new diagnosis for the given project_id by executing the LLMShapService
	to compute the diagnosis based on the initial prompt, questions and answers of the project.

	Parameters:
		project_id (int)
	Returns:
		int: The ID of the created diagnosis or None if an error occurs
	"""
	try:

		def construct_q_and_a_item(question: str, answer: str) -> str:
			return f"<Question>{question}</Question><Answer>{answer}</Answer>"

		# Construct the input for the LLMShapService
		initial_prompt = db.get_project_initial_prompt(project_id)
		if initial_prompt is None:
			raise ValueError("Initial prompt for project not found")
		questions: list[Question] = get_questions(project_id)
		answers: list[Answer] = get_answers(project_id)

		data = {
			"initial_prompt": initial_prompt,
		}

		for q in questions:
			# Find the corresponding answer for the question
			answer = next((a for a in answers if a["question_id"] == q["id"]), None)
			if answer is None:
				raise ValueError(f"No answer found for question ID {q['id']}")
			data[f"q{q['id']}"] = construct_q_and_a_item(q["question"], answer["answer"])

		# Execute the LLMShapService to compute the diagnosis
		config = LLMShapConfig(system_instruction=load_prompt())
		llmshap_service = LLMShapService(config=config)
		diagnosis, attribution = llmshap_service.compute_diagnosis(data)

		# Parse the diagnosis_result.output and save it to the databas
		print("Diagnosis result:", diagnosis)
		print("Attribution:", attribution)

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
		db.rollback() # type: ignore
		return None


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
				SELECT * FROM diagnosis_items 
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
				SELECT * FROM diagnosis_sentence_weights 
				WHERE diagnosis_id = %s;
				""",
			   (diagnosis_id,)
			)
			rows = cur.fetchall()
			return cast(list[DiagnosisSentenceWeight], [r for r in rows]) if rows else None
	except PsycopgError as e:
		print(f"Database error: {e}")
		return None