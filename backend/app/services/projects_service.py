from typing import cast, Optional, List, Any, TypedDict
from enum import Enum
from ..db import get_db
from psycopg.rows import dict_row
from psycopg import Connection, Error as PsycopgError


class ProjectStep(str, Enum):
	INITIAL_PROMPT = "INITIAL_PROMPT"
	INITIAL_QUESTIONS = "INITIAL_QUESTIONS"
	DIAGNOSIS = "DIAGNOSIS"


class Project(TypedDict):
    id: int
    title: str
    initial_prompt: str
    step: ProjectStep
    updated_at: Optional[str]
    created_at: Optional[str]


def get_project(project_id: int) -> Optional[Project]:
    try:
        db: Connection[dict[str, Any]] = get_db()
        with db.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM projects WHERE id = %s;", (project_id,))
            row = cur.fetchone()
            return cast(Project, row) if row else None
    except PsycopgError as e:
        print(f"Database error: {e}")
        return None


def create_project(title: str, initial_prompt: str) -> Optional[Project]:
    try:
        db: Connection[dict[str, Any]] = get_db()
        with db.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO projects (title, initial_prompt)
                VALUES (%s, %s)
                RETURNING *;
                """,
                (title, initial_prompt),
            )
            row = cur.fetchone()  # fetch before commit
        db.commit()
        return cast(Project, row) if row else None
    except PsycopgError as e:
        print(f"Database error: {e}")
        db.rollback() # type: ignore
        return None


def list_projects() -> List[Project]:
    try:
        db: Connection[dict[str, Any]] = get_db()
        with db.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT * FROM projects;
                """
            )
            rows = cur.fetchall()
            return [cast(Project, row) for row in rows]
    except PsycopgError as e:
        print(f"Database error: {e}")
        return []

def update_project_prompt(project_id: int, text: str) -> None:
	try:
		db: Connection[dict[str, Any]] = get_db()
		with db.cursor(row_factory=dict_row) as cur:
			cur.execute(
				"""
				UPDATE projects
				SET initial_prompt = %s, step = 'INITIAL_QUESTIONS'
				WHERE id = %s;
				""",
				(text, project_id)
			)
		db.commit()
	except PsycopgError as e:
		print(f"Database error: {e}")
		db.rollback()
