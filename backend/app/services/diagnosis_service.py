from typing import cast, Optional, Any, TypedDict
from enum import Enum

from backend.app.services.projects_service import Project, ProjectStep
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
		db.rollback() # type: ignore
		return None


def get_diagnosis(diagnosis_id: int) -> Optional[Diagnosis]:
	"""
	Returns the diagnosis for the given diagnosis_id
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


def get_diagnosis_list(project_id: int) -> list[Diagnosis]:
	"""
	Returns a list of diagnosis ids for the given project_id,
	ordered by created_at in descending order.
	"""
	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			cur.execute(
				"""
				SELECT * FROM diagnosis 
				WHERE project_id = %s
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