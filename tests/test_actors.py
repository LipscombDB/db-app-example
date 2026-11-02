from uuid import uuid4

from sqlalchemy import func, select, text

from app import MAX_NAME_LENGTH
from conftest import CSRF_TOKEN, TEST_LAST_NAME
from core import db
from models.schemas import Actor

def count_test_actors():
    return db.session.scalar(
        select(func.count()).select_from(Actor).where(Actor.last_name == TEST_LAST_NAME)
    )

# PAGES THAT ONLY READ DATA

def test_home_page_lists_actors(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Actors' in response.data

def test_get_actors_returns_json(client):
    response = client.get('/get_actors')
    assert response.status_code == 200
    assert 'first_name' in response.get_json()[0]

# ADDING AN ACTOR

def test_add_actor(csrf_client, created_actor_ids):
    actor_count = count_test_actors()
    first_name = f'Ada-{uuid4().hex[:12]}'
    response = csrf_client.post('/add', data={
        'first_name': first_name,
        'last_name': TEST_LAST_NAME,
        'csrf_token': CSRF_TOKEN,
    })
    actor_id = db.session.scalar(
        select(Actor.actor_id).where(
            Actor.first_name == first_name,
            Actor.last_name == TEST_LAST_NAME,
        )
    )
    if actor_id is not None:
        created_actor_ids.append(actor_id)
    assert response.status_code == 302
    assert actor_id is not None
    assert count_test_actors() == actor_count + 1

def test_add_actor_with_blank_name_is_rejected(csrf_client):
    actor_count = count_test_actors()
    response = csrf_client.post('/add', data={
        'first_name': '   ',
        'last_name': TEST_LAST_NAME,
        'csrf_token': CSRF_TOKEN,
    }, follow_redirects=True)
    assert b'Please enter both a first name and a last name.' in response.data
    assert count_test_actors() == actor_count

def test_add_actor_with_long_name_is_rejected(csrf_client):
    actor_count = count_test_actors()
    response = csrf_client.post('/add', data={
        'first_name': 'A' * (MAX_NAME_LENGTH + 1),
        'last_name': TEST_LAST_NAME,
        'csrf_token': CSRF_TOKEN,
    }, follow_redirects=True)
    assert b'Names can be at most' in response.data
    assert count_test_actors() == actor_count

# DELETING AN ACTOR

def test_delete_actor(csrf_client, created_actor_ids):
    actor_count = count_test_actors()
    actor = Actor(first_name='Ada', last_name=TEST_LAST_NAME, last_update=func.now())
    db.session.add(actor)
    db.session.commit()
    created_actor_ids.append(actor.actor_id)

    response = csrf_client.post(f'/delete/{actor.actor_id}', data={'csrf_token': CSRF_TOKEN})
    assert response.status_code == 302
    assert count_test_actors() == actor_count

def test_delete_actor_in_films_shows_message(csrf_client):
    actor_id = db.session.scalar(text("SELECT actor_id FROM film_actor LIMIT 1"))

    response = csrf_client.post(f'/delete/{actor_id}', data={'csrf_token': CSRF_TOKEN},
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'appear in one or more films' in response.data
    assert db.session.get(Actor, actor_id) is not None

def test_delete_missing_actor_returns_404(csrf_client):
    missing_id = db.session.scalar(select(func.max(Actor.actor_id))) + 1000
    response = csrf_client.post(f'/delete/{missing_id}', data={'csrf_token': CSRF_TOKEN})
    assert response.status_code == 404

def test_delete_is_post_only(client):
    response = client.get('/delete/1')
    assert response.status_code == 405

# CSRF PROTECTION

def test_post_without_csrf_token_is_rejected(csrf_client):
    actor_count = count_test_actors()
    response = csrf_client.post('/add', data={
        'first_name': 'Ada',
        'last_name': TEST_LAST_NAME,
    })
    assert response.status_code == 400
    assert count_test_actors() == actor_count

def test_post_with_wrong_csrf_token_is_rejected(csrf_client):
    actor_count = count_test_actors()
    response = csrf_client.post('/add', data={
        'first_name': 'Ada',
        'last_name': TEST_LAST_NAME,
        'csrf_token': 'wrong',
    })
    assert response.status_code == 400
    assert count_test_actors() == actor_count
