"""Loan intake service — FastAPI over PostgreSQL."""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from db import get_conn

app = FastAPI(title="Loan Intake Service", version="2.0.0")

# ── CORS ────────────────────────────────────────────────────────
# Our page is served from one port and this API listens on another.
# Because the ports differ, browsers treat them as different ORIGINS
# and block the page from reading our responses until we opt in.
# The browser enforces this, not FastAPI — the same request from curl
# works fine either way.
#
# The origin is read from the environment because the web port is
# configurable (see .env). Hard-coding 3000 here means CORS silently
# breaks the moment someone has to move the website off that port.
WEB_ORIGIN = os.environ.get("WEB_ORIGIN", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[WEB_ORIGIN],  # never "*" in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models: unchanged from version 1 ────────────────────────────

class ApplicationIn(BaseModel):
    applicant_name: str = Field(min_length=2, max_length=100)
    monthly_income: float = Field(gt=0)
    amount_requested: float = Field(gt=0, le=10_00_000)
    purpose: str = Field(min_length=2, max_length=50)


class ApplicationOut(ApplicationIn):
    id: int
    status: str = "received"


# ── Routes ──────────────────────────────────────────────────────

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/applications", response_model=list[ApplicationOut])
def list_applications() -> list[ApplicationOut]:
    """Read every application, oldest first."""
    # 'with' guarantees the connection closes even if an error is raised.
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM applications ORDER BY id"
        ).fetchall()
    # Each row is a dict, so ** unpacks it into keyword arguments.
    return [ApplicationOut(**row) for row in rows]


@app.post("/applications", response_model=ApplicationOut, status_code=201)
def create_application(payload: ApplicationIn) -> ApplicationOut:
    """Insert one application and return it, id included."""
    with get_conn() as conn:
        row = conn.execute(
            # %(name)s placeholders — NEVER an f-string. The driver
            # sends the query shape and the values separately, so a
            # value can never be read as SQL. This is what prevents
            # SQL injection.
            """
            INSERT INTO applications
                (applicant_name, monthly_income,
                 amount_requested, purpose)
            VALUES
                (%(applicant_name)s, %(monthly_income)s,
                 %(amount_requested)s, %(purpose)s)
            RETURNING *
            """,
            payload.model_dump(),   # the model as a plain dict
        ).fetchone()
        conn.commit()               # make the change permanent
    return ApplicationOut(**row)


@app.get("/applications/{app_id}", response_model=ApplicationOut)
def get_application(app_id: int) -> ApplicationOut:
    """Read one application by id, or 404."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM applications WHERE id = %(id)s",
            {"id": app_id},
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return ApplicationOut(**row)