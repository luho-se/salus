from typing import cast, Optional, List, Any, TypedDict
from enum import Enum

from backend.app.services.projects_service import ProjectStep
from ..db import get_db
from psycopg.rows import dict_row
from psycopg import Connection, Error as PsycopgError

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

	return

def get_diagnosis_list(project_id: int) -> List[int]:
	return