-- Runs ONCE, on first initialisation of an empty database.
-- This is not a migration system: editing it later will not change
-- an existing database. Real projects use migration tools instead.

CREATE TABLE IF NOT EXISTS applications (
    -- SERIAL PRIMARY KEY: Postgres assigns a unique, auto-incrementing
    -- id. The client never invents one.
    id               SERIAL PRIMARY KEY,
    applicant_name   TEXT    NOT NULL,

    -- The CHECK is the same rule as Pydantic's gt=0, one layer deeper.
    -- Defence in depth: Pydantic gives the user a friendly error, this
    -- holds even for data that never came through our API.
    monthly_income   NUMERIC NOT NULL CHECK (monthly_income > 0),
    amount_requested NUMERIC NOT NULL CHECK (amount_requested > 0),
    purpose          TEXT    NOT NULL,
    status           TEXT    NOT NULL DEFAULT 'received'
);

-- Two seed rows, so the page has something to show immediately.
INSERT INTO applications
    (applicant_name, monthly_income, amount_requested, purpose)
VALUES
    ('Asha Traders',    45000, 300000, 'working_capital'),
    ('Ravi Auto Works', 62000, 450000, 'equipment');