# Loan Intake — Python + FastAPI + Next.js + PostgreSQL, all in Docker

Three containers on one private Compose network:

```
browser ──► web  (Next.js)  ──► api (FastAPI) ──► db (PostgreSQL)
            :3000               :8001              :5433
              ▲                   ▲                  ▲
              └── these are HOST ports, set in .env ─┘
```

## Run it

```bash
docker compose up --build
```

Then open <http://localhost:3000>. The API docs are at
<http://localhost:8001/docs>.

Stop with `Ctrl-C`, then `docker compose down`.

## Changing ports

**One file: [`.env`](.env).** Change the number, re-run
`docker compose up --build`. Nothing else needs editing — the compose
file, the CORS rule, and the browser's API URL are all derived from it.

| Variable   | Default | What it is                              |
| ---------- | ------- | --------------------------------------- |
| `DB_PORT`  | `5433`  | PostgreSQL, for psql/DBeaver from your laptop |
| `API_PORT` | `8001`  | FastAPI                                 |
| `WEB_PORT` | `3000`  | the website                             |

Why these defaults on this machine: `5432` is your existing local
Postgres and `8000` is another project's uvicorn, so both are moved up
by one.

### The one rule that trips everyone up

Ports come in pairs — `"5433:5432"` is `HOST:CONTAINER`.

* **Containers talk to each other on the CONTAINER port**, by service
  name: the api reaches the database at `db:5432`. It does this over
  the private network, where the published port does not exist.
* **Your browser talks on the HOST port**: `localhost:8001`.

So `DATABASE_URL` says `db:5432` even though the database is published
on 5433, and `NEXT_PUBLIC_API_URL` says `localhost:8001` even though the
api listens on 8000 inside its container. Both look wrong at a glance
and both are correct.

If you change `DB_PORT` to anything, `DATABASE_URL` still says
`db:5432`. It never changes.

## Checking a port is free before you pick it

```bash
lsof -nP -iTCP:8001 -sTCP:LISTEN
```

No output means the port is free.

## Running the tests

The tests need the database, so run them on the compose network:

```bash
docker compose run --rm api pytest -v
```

They truncate the `applications` table and restore the two seed rows
when finished.

## Resetting the database

`db/init.sql` runs **only** when the data volume is empty. Editing it
later changes nothing. To start clean:

```bash
docker compose down -v && docker compose up --build
```
