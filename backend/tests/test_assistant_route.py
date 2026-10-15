import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import assistant as assistant_route
from app.api.routes import auth
from app.core.database import get_db
from app.core.rate_limit import RateLimiter


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


def ask(client, token=None, text="Мен китеп окуймун.", question="Is this easy?"):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return client.post(
        "/assistant",
        headers=headers,
        json={"text": text, "question": question, "language": "en"},
    )


def test_assistant_requires_login(assistant_client, fake_model):
    assert ask(assistant_client).status_code == 401
    assert fake_model == []  # the model was never called


def test_assistant_rejects_a_bad_token(assistant_client, fake_model):
    assert ask(assistant_client, token="garbage").status_code == 401
    assert fake_model == []


def test_assistant_answers_a_logged_in_user(assistant_client):
    token = make_user_and_token(assistant_client)
    response = ask(assistant_client, token)
    assert response.status_code == 200
    assert response.json() == {"answer": "fake answer", "tools_used": ["analyze_readability"]}


def test_assistant_limits_each_user(assistant_client, fake_model):
    token = make_user_and_token(assistant_client)
    assert [ask(assistant_client, token).status_code for _ in range(3)] == [200, 200, 200]
    response = ask(assistant_client, token)
    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0
    assert len(fake_model) == 3  # the refused request never reached the model


def test_another_user_is_not_affected_by_the_limit(assistant_client):
    first = make_user_and_token(assistant_client, email="a@example.com")
    second = make_user_and_token(assistant_client, email="b@example.com")
    for _ in range(3):
        ask(assistant_client, first)
    assert ask(assistant_client, first).status_code == 429
    assert ask(assistant_client, second).status_code == 200


def test_empty_requests_do_not_use_up_the_limit(assistant_client, fake_model):
    token = make_user_and_token(assistant_client)
    for _ in range(5):
        assert ask(assistant_client, token, text="   ").status_code == 400
    assert ask(assistant_client, token).status_code == 200
    assert len(fake_model) == 1