from typing import cast, Optional, Any, TypedDict
from enum import Enum

from backend.app.services.projects_service import Project
from backend.app.services.projects_service import ProjectStep
from backend.app.services.questions_service import get_questions
from backend.app.services.questions_service import get_answers
from backend.app.services.questions_service import Question
from backend.app.services.questions_service import Answer
from backend.app.modules.xai_module.llmshap_service import LLMShapService
from ..db import get_db
from psycopg.rows import dict_row
from psycopg import Connection, Error as PsycopgError

from backend.app import db


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
		# Construct the input for the LLMShapService
		initial_prompt = db.get_project_initial_prompt(project_id)
		if initial_prompt is None:
			raise ValueError("Initial prompt for project not found")
		questions: list[Question] = get_questions(project_id)
		answers: list[Answer] = get_answers(project_id)

		data = {
			"initial_prompt": initial_prompt,
			"q_and_a_items": []
		}
		for q in questions:
			a = next((a for a in answers if a["question_id"] == q["id"]), None)
			if a is not None:
				data["q_and_a_items"].append((q["question"], a["answer"]))

		# Execute the LLMShapService to compute the diagnosis
		llmshap_service = LLMShapService()
		diagnosis_result = llmshap_service.compute_diagnosis(data)
		print("Diagnosis result:", diagnosis_result)

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