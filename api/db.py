"""Database connection helper.

Kept separate from main.py so the routes stay readable.
"""

import os

import psycopg
from psycopg.rows import dict_row

# Read the connection string from the environment, with a sensible
# local default. Docker Compose sets this variable in Part 6 — which
# is how the same code works both on your machine and in a container.
#
# Format: postgresql://user:password@host:port/database
#
# Two different addresses reach the same database:
#   in Docker  -> db:5432          (service name, internal port)
#   on laptop  -> localhost:5433   (the PUBLISHED port from .env)
# The fallback below is the laptop one, so `uvicorn main:app` still
# works outside Docker. DB_PORT keeps it in step with .env.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"postgresql://intake:intake@localhost:{os.environ.get('DB_PORT', '5433')}/intake",
)


def get_conn() -> psycopg.Connection:
    """Open a new connection.

    row_factory=dict_row makes each result row a dict rather than a
    plain tuple, so we can write ApplicationOut(**row) instead of
    unpacking by position.

    One connection per request is fine at this scale. A production
    service would use a connection pool.
    """
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)