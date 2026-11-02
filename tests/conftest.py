# Shared setup for the tests. pytest finds this file automatically
# and passes the fixtures below to any test that names them as a parameter.
#
# The tests use the same MySQL database as the app (set in .env).
# Every actor a test adds uses TEST_LAST_NAME, and those rows are
# deleted after each test, so the sakila data is left unchanged.

import pytest
from sqlalchemy import delete

from app import app as flask_app
from core import db
from models.schemas import Actor

TEST_LAST_NAME = "PYTEST-TEMP"
CSRF_TOKEN = "test-token"

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    with flask_app.app_context():
        yield flask_app
        # Clean up any actors the test added
        db.session.rollback()
        db.session.execute(delete(Actor).where(Actor.last_name == TEST_LAST_NAME))
        db.session.commit()

# A test client sends requests to the app without starting a server
@pytest.fixture
def client(app):
    return app.test_client()

# A test client whose session already holds a CSRF token,
# so its POST requests can include a matching csrf_token field
@pytest.fixture
def csrf_client(client):
    with client.session_transaction() as session:
        session['csrf_token'] = CSRF_TOKEN
    return client
