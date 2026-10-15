from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.core.security import ALGORITHM
from app.models.user import User


def register(client, email="test@example.com", password="correct horse 1"):
    return client.post("/auth/register", json={"email": email, "password": password})


def login(client, email="test@example.com", password="correct horse 1"):
    # the login endpoint takes a form (not JSON), and the email goes in the "username" field
    return client.post("/auth/login", data={"username": email, "password": password})


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def future():
    return datetime.now(timezone.utc) + timedelta(hours=1)


# ---- login ----

def test_login_returns_a_token_for_the_user(client):
    user_id = register(client).json()["id"]
    response = login(client)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    payload = jwt.decode(body["access_token"], settings.secret_key, algorithms=[ALGORITHM])
    assert payload["sub"] == str(user_id)


def test_login_email_is_case_insensitive(client):
    register(client)
    assert login(client, email="  TEST@Example.com ").status_code == 200


def test_login_with_cyrillic_password(client):
    register(client, password="тест12345")
    assert login(client, password="тест12345").status_code == 200


def test_login_wrong_password_returns_401(client):
    register(client)
    response = login(client, password="wrong password 1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_unknown_email_gives_the_same_401(client):
    register(client)
    wrong_password = login(client, password="wrong password 1")
    unknown_email = login(client, email="nobody@example.com")
    assert unknown_email.status_code == 401
    assert unknown_email.json() == wrong_password.json()


# ---- /auth/me ----

def test_me_returns_the_logged_in_user(client):
    register(client)
    token = login(client).json()["access_token"]
    response = client.get("/auth/me", headers=auth_header(token))
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "test@example.com"
    assert body["role"] == "reader"
    assert "hashed_password" not in body


def test_me_without_a_token_returns_401(client):
    assert client.get("/auth/me").status_code == 401


def test_me_with_a_tampered_token_returns_401(client):
    register(client)
    token = login(client).json()["access_token"]
    forged = token[:-3] + ("abc" if token[-3:] != "abc" else "xyz")
    assert client.get("/auth/me", headers=auth_header(forged)).status_code == 401


def test_me_with_an_expired_token_returns_401(client):
    user_id = register(client).json()["id"]
    expired = jwt.encode(
        {"sub": str(user_id), "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.secret_key,
        algorithm=ALGORITHM,
    )
    assert client.get("/auth/me", headers=auth_header(expired)).status_code == 401


def test_me_for_a_deleted_user_returns_401(client, db_session):
    register(client)
    token = login(client).json()["access_token"]
    user = db_session.query(User).filter(User.email == "test@example.com").first()
    db_session.delete(user)
    db_session.commit()
    assert client.get("/auth/me", headers=auth_header(token)).status_code == 401


def test_me_with_a_non_numeric_subject_returns_401(client):
    token = jwt.encode(
        {"sub": "abc", "exp": future()}, settings.secret_key, algorithm=ALGORITHM
    )
    assert client.get("/auth/me", headers=auth_header(token)).status_code == 401


def test_me_with_a_token_that_never_expires_returns_401(client):
    user_id = register(client).json()["id"]
    token = jwt.encode({"sub": str(user_id)}, settings.secret_key, algorithm=ALGORITHM)
    assert client.get("/auth/me", headers=auth_header(token)).status_code == 401


