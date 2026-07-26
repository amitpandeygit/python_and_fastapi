"""Tests for the loan intake service.

The service now stores data in PostgreSQL, so these tests need a
database. Run them the same way the app runs — inside Docker:

    docker compose run --rm api pytest -v

(That starts a throwaway api container on the compose network, so
`db:5432` resolves. Running bare `pytest` on your laptop works too,
as long as the db container is up and DATABASE_URL points at the
published port from .env.)
"""

import pytest
from fastapi.testclient import TestClient

from db import get_conn
from main import app

# TestClient drives the app IN-PROCESS: no server starts, no port is
# opened. The database, however, is real — that is the trade for
# testing the SQL rather than a fake.
client = TestClient(app)

# The rows db/init.sql seeds. We put them back at the end so the demo
# page still has something to show after a test run.
SEED = [
    ("Asha Traders", 45000, 300000, "working_capital"),
    ("Ravi Auto Works", 62000, 450000, "equipment"),
]


@pytest.fixture(autouse=True)
def clean_table():
    """Runs automatically before EVERY test in this file.

    Clearing shared state is what keeps tests independent. Without it,
    tests pass alone and fail together — the worst kind of test suite,
    because the result depends on the order they happen to run in.

    RESTART IDENTITY also resets the SERIAL counter, so the first row
    inserted in each test is reliably id 1.
    """
    with get_conn() as conn:
        conn.execute("TRUNCATE applications RESTART IDENTITY")
        conn.commit()
    yield


@pytest.fixture(scope="session", autouse=True)
def restore_seed_rows():
    """After the whole run, put the demo data back."""
    yield
    with get_conn() as conn:
        conn.execute("TRUNCATE applications RESTART IDENTITY")
        # executemany lives on the cursor, not the connection.
        conn.cursor().executemany(
            """
            INSERT INTO applications
                (applicant_name, monthly_income,
                 amount_requested, purpose)
            VALUES (%s, %s, %s, %s)
            """,
            SEED,
        )
        conn.commit()


def test_health():
    """The endpoint Compose uses as the api's healthcheck."""
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_list_application():
    """The happy path: a valid application is created, then listed."""
    payload = {
        "applicant_name": "Asha Traders",
        "monthly_income": 45000,
        "amount_requested": 300000,
        "purpose": "working_capital",
    }

    created = client.post("/applications", json=payload)
    assert created.status_code == 201            # created, not 200
    body = created.json()
    assert body["id"] == 1                       # the database assigned it
    assert body["status"] == "received"          # default applied
    assert body["applicant_name"] == "Asha Traders"

    listed = client.get("/applications")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_negative_income_is_rejected():
    """The contract: invalid input never becomes a stored application."""
    bad = {
        "applicant_name": "X Ltd",
        "monthly_income": -1,                    # violates gt=0
        "amount_requested": 1000,
        "purpose": "vehicle",
    }
    response = client.post("/applications", json=bad)
    assert response.status_code == 422

    # And nothing was stored as a side effect.
    assert client.get("/applications").json() == []


def test_missing_application_returns_404():
    """A valid request for something that does not exist."""
    assert client.get("/applications/999").status_code == 404
