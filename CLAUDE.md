# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A small teaching Flask app (course example) that reads and writes actor data in the MySQL `sakila` sample database. Code is intentionally simple and heavily commented for students; keep that style and keep README.md's step-by-step setup instructions accurate for beginners on macOS and Windows when changing setup or configuration.

## Commands

```
source venv/bin/activate          # required; the app exits if not in a venv
pip install -r requirements.txt   # versions are pinned
python app.py                     # serves http://127.0.0.1:8000
pytest                            # run all tests
pytest tests/test_actors.py::test_add_actor   # run one test
```

There is no linter or build step. After adding a package, regenerate `requirements.txt` with `pip freeze > requirements.txt` from inside the venv.

## Tests

pytest with Flask's `test_client()`; `pytest.ini` sets `pythonpath = .` so tests import `app`, `core`, `models` directly. Tests run against the real MySQL database from `.env` (not SQLite: the models map onto sakila's existing tables and the `actor_info` view, and delete behaviour relies on MySQL's `film_actor` foreign key). Fixtures in `tests/conftest.py`:
- `app` pushes an app context and, on teardown, deletes every actor whose `last_name` is `TEST_LAST_NAME`. Any actor a test creates must use that last name so the sakila data stays unchanged.
- `csrf_client` pre-seeds the session with `CSRF_TOKEN`; POSTs must send it as the `csrf_token` form field or they get a 400.

Configuration comes from `.env` (git-ignored): `PASSWORD` (required; the app exits with a message if missing), optional `DB_USER` (default `root`), `DB_NAME` (default `sakila`), and `FLASK_DEBUG=1` to enable the reloader/debugger. Host and port (`127.0.0.1:3306`) are hard-coded in `db_cred` in `core/__init__.py`. Running requires a local MySQL with sakila installed.

## Architecture

- `core/__init__.py` does all setup at import time, in this order: virtualenv check (must stay before any third-party imports), `.env` loading and validation, Flask app creation (`template_folder="../templates"`), DB URI via `sqlalchemy.URL.create` (escapes special characters in the password), and the `db` (Flask-SQLAlchemy, SQLAlchemy 2.0 `DeclarativeBase`) and `ma` (Marshmallow) instances. Everything else imports `app`, `db`, `ma` from `core`.
- `models/schemas.py` holds the ORM classes, mapped onto existing sakila objects (no migrations or `create_all`). Table names come from Flask-SQLAlchemy's automatic CamelCase→snake_case naming: `Actor` → `actor` table, `ActorInfo` → the `actor_info` view (read-only).
- `models/Actor.py` and `models/ActorInfo.py` are per-entity data-access modules (no `models/__init__.py`; `app.py` imports them as modules via `from models import Actor, ActorInfo`). Each defines query functions plus a `SQLAlchemyAutoSchema`; functions return schema-dumped dicts, so JSON routes can return them directly.
- `app.py` holds all routes. Conventions established there:
  - Hand-rolled CSRF protection: a `context_processor` puts `csrf_token` into every template and a `before_request` hook rejects any POST without a matching `csrf_token` form field. Every new POST form must include `<input type="hidden" name="csrf_token" value="{{ csrf_token }}">`.
  - State-changing routes are POST-only; validation errors use `flash()` + redirect (templates render `get_flashed_messages()`).
  - `MAX_NAME_LENGTH = 45` mirrors sakila's `VARCHAR(45)` columns.
  - `Actor.delete_actor` returns `False` on `IntegrityError` (actor referenced by `film_actor`) so the route can flash a message instead of a 500; it uses `db.get_or_404` for missing IDs.
- `app.secret_key` is regenerated each run, so sessions/CSRF tokens don't survive a restart (intended for local use).
