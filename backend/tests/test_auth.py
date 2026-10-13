from app.models.user import User


def register(client, email="test@example.com", password="correct horse 1"):
    return client.post("/auth/register", json={"email": email, "password": password})


def test_register_succeeds_and_hides_password(client):
    response = register(client, email="  Test@Example.com ", password="тест12345")
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "test@example.com"
    assert body["role"] == "reader"
    assert "password" not in body
    assert "hashed_password" not in body


def test_duplicate_email_returns_409_even_with_different_case(client):
    assert register(client).status_code == 201
    response = register(client, email="TEST@example.com")
    assert response.status_code == 409


def test_short_password_returns_422(client):
    assert register(client, password="short").status_code == 422


def test_password_over_72_bytes_returns_422(client):
    assert register(client, password="a" * 73).status_code == 422


def test_cyrillic_password_limit_is_counted_in_bytes(client):
    # each Cyrillic letter is 2 bytes in UTF-8: 36 letters = 72 bytes (allowed), 37 = 74 (rejected)
    assert register(client, email="a@example.com", password="я" * 36).status_code == 201
    assert register(client, email="b@example.com", password="я" * 37).status_code == 422


def test_invalid_email_returns_422(client):
    assert register(client, email="not-an-email").status_code == 422


def test_password_is_stored_as_bcrypt_hash(client, db_session):
    register(client, password="correct horse 1")
    user = db_session.query(User).filter(User.email == "test@example.com").first()
    assert user.hashed_password != "correct horse 1"
    assert user.hashed_password.startswith("$2b$")
