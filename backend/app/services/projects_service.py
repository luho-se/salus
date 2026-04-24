from typing import cast, Optional, List
from db import get_db
from psycopg.rows import dict_row
from psycopg import Connection, Error as PsycopgError
from typing import TypedDict

class Project(TypedDict):
    id: int
    title: str
    initial_prompt: Optional[str]
    step: str
    updated_at: str
    created_at: str

def get_project(project_id: int) -> Optional[Project]:
    try:
        db: Connection = get_db()
        with db.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM project WHERE id = %s;", (project_id,))
            row = cur.fetchone()
            return cast(Project, row) if row else None
    except PsycopgError as e:
        print(f"Database error: {e}")
        return None

def create_project(title: str, initial_prompt: str) -> Optional[Project]:
    db: Connection | None = None
    try:
        db = get_db()
        with db.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO project (title, initial_prompt)
                VALUES (%s, %s)
                RETURNING *;
                """,
                (title, initial_prompt)
            )
            db.commit()
            row = cur.fetchone()
            return cast(Project, row) if row else None
    except PsycopgError as e:
        print(f"Database error: {e}")
        if db is not None:
            db.rollback()
        return None

def list_projects() -> List[Project]:
    try:
        db: Connection = get_db()
        with db.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM project;")
            rows = cur.fetchall()
            return [cast(Project, row) for row in rows]
    except PsycopgError as e:
        print(f"Database error: {e}")
        return []
