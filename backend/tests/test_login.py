from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.core.security import ACCESS_TOKEN_COOKIE, ALGORITHM
from app.models.user import User


def register(client, email="test@example.com", password="correct horse 1"):
    return client.post("/auth/register", json={"email": email, "password": password})


def login(client, email="test@example.com", password="correct horse 1"):
    # the login endpoint takes a form (not JSON), and the email goes in the "username" field
    return client.post("/auth/login", data={"username": email, "password": password})


def set_cookie_token(client, token):
    # replace whatever cookie the client holds with this exact value
    client.cookies.clear()
    client.cookies.set(ACCESS_TOKEN_COOKIE, token)


def future():
    return datetime.now(timezone.utc) + timedelta(hours=1)


# ---- login ----

def test_login_sets_a_secure_cookie_and_returns_the_user(client):
    user_id = register(client).json()["id"]
    response = login(client)
    assert response.status_code == 200

    body = response.json()
    assert body == {"id": user_id, "email": "test@example.com", "role": "reader"}
    assert "access_token" not in body  # the token only travels in the cookie

    set_cookie = response.headers["set-cookie"].lower()
    assert f"{ACCESS_TOKEN_COOKIE}=" in set_cookie
    assert "httponly" in set_cookie
    assert "samesite=lax" in set_cookie
    assert "max-age=86400" in set_cookie

    token = client.cookies.get(ACCESS_TOKEN_COOKIE)
    payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
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


def test_failed_login_sets_no_cookie(client):
    register(client)
    response = login(client, password="wrong password 1")
    assert "set-cookie" not in response.headers
    assert client.get("/auth/me").status_code == 401


# ---- logout ----

def test_logout_clears_the_cookie(client):
    register(client)
    login(client)
    assert client.get("/auth/me").status_code == 200

    response = client.post("/auth/logout")

    assert response.status_code == 204
    assert "max-age=0" in response.headers["set-cookie"].lower()
    assert client.get("/auth/me").status_code == 401


def test_logout_without_being_logged_in_is_fine(client):
    assert client.post("/auth/logout").status_code == 204


# ---- /auth/me ----

def test_me_returns_the_logged_in_user(client):
    register(client)
    login(client)
    response = client.get("/auth/me")
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "test@example.com"
    assert body["role"] == "reader"
    assert "hashed_password" not in body


def test_me_without_a_cookie_returns_401(client):
    assert client.get("/auth/me").status_code == 401


def test_me_ignores_the_authorization_header(client):
    register(client)
    login(client)
    token = client.cookies.get(ACCESS_TOKEN_COOKIE)
    client.cookies.clear()
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_me_with_a_tampered_token_returns_401(client):
    register(client)
    login(client)
    token = client.cookies.get(ACCESS_TOKEN_COOKIE)
    forged = token[:-3] + ("abc" if token[-3:] != "abc" else "xyz")
    set_cookie_token(client, forged)
    assert client.get("/auth/me").status_code == 401


def test_me_with_an_expired_token_returns_401(client):
    user_id = register(client).json()["id"]
    expired = jwt.encode(
        {"sub": str(user_id), "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.secret_key,
        algorithm=ALGORITHM,
    )
    set_cookie_token(client, expired)
    assert client.get("/auth/me").status_code == 401


def test_me_for_a_deleted_user_returns_401(client, db_session):
    register(client)
    login(client)
    user = db_session.query(User).filter(User.email == "test@example.com").first()
    db_session.delete(user)
    db_session.commit()
    assert client.get("/auth/me").status_code == 401


def test_me_with_a_non_numeric_subject_returns_401(client):
    token = jwt.encode(
        {"sub": "abc", "exp": future()}, settings.secret_key, algorithm=ALGORITHM
    )
    set_cookie_token(client, token)
    assert client.get("/auth/me").status_code == 401


def test_me_with_a_token_that_never_expires_returns_401(client):
    user_id = register(client).json()["id"]
    token = jwt.encode({"sub": str(user_id)}, settings.secret_key, algorithm=ALGORITHM)
    set_cookie_token(client, token)
    assert client.get("/auth/me").status_code == 401
