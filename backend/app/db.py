from typing import Any, cast

from flask import Flask, current_app, g
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

pool: ConnectionPool[Any] | None = None

def get_pool() -> ConnectionPool[Any]:
    global pool
    if pool is None:
        database_url = cast(str, current_app.config["DATABASE_URL"])

        pool = ConnectionPool(
            conninfo=database_url,
            kwargs={"row_factory": dict_row},
            min_size=1,
            max_size=10,
        )
    return pool

def get_db() -> psycopg.Connection:
    if "db" not in g:
        g.db = get_pool().getconn()
    return g.db

def close_db(_: BaseException | None = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        get_pool().putconn(db)

def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
