from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.utils.api import get_current_user, get_iam, router
from app.utils.iam import IAM
from app.utils.user import User


app = FastAPI()
app.include_router(router)


def make_client():
    iam = MagicMock(spec=IAM)
    app.dependency_overrides[get_iam] = lambda: iam
    return TestClient(app), iam


def test_login_returns_token():
    client, iam = make_client()
    iam.check_user.return_value = True
    iam.get_user.return_value = User('student', 'Test', 'User')

    response = client.post(
        '/token',
        data={'username': 'student', 'password': 'Password123!'},
    )

    assert response.status_code == 200
    assert response.json()['token_type'] == 'bearer'
    assert response.json()['access_token']
    app.dependency_overrides.clear()


def test_login_rejects_bad_password():
    client, iam = make_client()
    iam.check_user.return_value = False

    response = client.post(
        '/token',
        data={'username': 'student', 'password': 'wrong'},
    )

    assert response.status_code == 401
    app.dependency_overrides.clear()


def test_registration_requires_admin():
    client, _ = make_client()
    app.dependency_overrides[get_current_user] = lambda: User('student', 'Test', 'User')

    response = client.post('/register', json={
        'username': 'new_user',
        'password': 'Password123!',
        'first_name': 'New',
        'last_name': 'User',
    })

    assert response.status_code == 403
    app.dependency_overrides.clear()


def test_admin_can_register_user():
    client, iam = make_client()
    app.dependency_overrides[get_current_user] = lambda: User(
        'teacher', 'Test', 'Teacher', admin=True
    )
    iam.is_suitable.return_value = (True, '')
    iam.create_user.return_value = (True, 'User created successfully.')
    iam.get_user.return_value = User('new_user', 'New', 'User')

    response = client.post('/register', json={
        'username': 'new_user',
        'password': 'Password123!',
        'first_name': 'New',
        'last_name': 'User',
    })

    assert response.status_code == 201
    assert response.json()['username'] == 'new_user'
    app.dependency_overrides.clear()
