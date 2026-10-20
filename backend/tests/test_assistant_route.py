import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import assistant as assistant_route
from app.api.routes import auth
from app.core.database import get_db
from app.core.rate_limit import RateLimiter
from app.core.security import ACCESS_TOKEN_COOKIE


@pytest.fixture
def fake_model(monkeypatch):
    calls = []

    def fake_ask(text, question, language):
        calls.append((text, question, language))
        return {"answer": "fake answer", "tools_used": ["analyze_readability"]}

    monkeypatch.setattr(assistant_route, "ask_assistant", fake_ask)
    return calls


@pytest.fixture
def assistant_client(db_session, fake_model, monkeypatch):
    # a fresh, small limiter for every test
    monkeypatch.setattr(
        assistant_route, "assistant_limiter", RateLimiter(max_requests=3, window_seconds=3600)
    )
    app = FastAPI()
    app.include_router(auth.router)
    app.include_router(assistant_route.router)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def make_user_and_token(client, email="test@example.com", password="correct horse 1"):
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", data={"username": email, "password": password})
    return response.json()["access_token"]

def log_in(client, email="test@example.com", password="correct horse 1"):
    # the test client keeps the login cookie and sends it with later requests
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200


def ask(client, text="Мен китеп окуймун.", question="Is this easy?"):
    return client.post(
        "/assistant",
        json={"text": text, "question": question, "language": "en"},
    )


def test_assistant_requires_login(assistant_client, fake_model):
    assert ask(assistant_client).status_code == 401
    assert fake_model == []  # the model was never called


def test_assistant_rejects_a_bad_cookie(assistant_client, fake_model):
    assistant_client.cookies.set(ACCESS_TOKEN_COOKIE, "garbage")
    assert ask(assistant_client).status_code == 401
    assert fake_model == []


def test_assistant_answers_a_logged_in_user(assistant_client):
    log_in(assistant_client)
    response = ask(assistant_client)
    assert response.status_code == 200
    assert response.json() == {"answer": "fake answer", "tools_used": ["analyze_readability"]}


def test_assistant_limits_each_user(assistant_client, fake_model):
    log_in(assistant_client)
    assert [ask(assistant_client).status_code for _ in range(3)] == [200, 200, 200]
    response = ask(assistant_client)
    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0
    assert len(fake_model) == 3  # the refused request never reached the model


def test_another_user_is_not_affected_by_the_limit(assistant_client):
    log_in(assistant_client, email="a@example.com")
    for _ in range(3):
        ask(assistant_client)
    assert ask(assistant_client).status_code == 429
    log_in(assistant_client, email="b@example.com")  # new login replaces the cookie
    assert ask(assistant_client).status_code == 200


def test_empty_requests_do_not_use_up_the_limit(assistant_client, fake_model):
    log_in(assistant_client)
    for _ in range(5):
        assert ask(assistant_client, text="   ").status_code == 400
    assert ask(assistant_client).status_code == 200
    assert len(fake_model) == 1
