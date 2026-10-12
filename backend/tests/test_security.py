import unicodedata

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    ALGORITHM,
    create_access_token,
    hash_password,
    verify_password,
)


def test_password_round_trip():
    hashed = hash_password("correct horse battery")
    assert hashed != "correct horse battery"
    assert verify_password("correct horse battery", hashed)
    assert not verify_password("wrong password", hashed)


def test_cyrillic_password_works():
    hashed = hash_password("жомоктор123")
    assert verify_password("жомоктор123", hashed)


def test_equivalent_unicode_forms_match():
    composed = "жомоктор\u0439"  # й as one character
    decomposed = unicodedata.normalize("NFD", composed)  # и + combining mark
    assert composed != decomposed
    hashed = hash_password(composed)
    assert verify_password(decomposed, hashed)


def test_password_over_72_bytes_is_rejected():
    too_long = "a" * 73
    with pytest.raises(ValueError):
        hash_password(too_long)
    assert not verify_password(too_long, hash_password("short password"))


def test_token_contains_user_id_and_expiry():
    token = create_access_token(42)
    payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    assert payload["sub"] == "42"
    assert "exp" in payload


def test_tampered_token_is_rejected():
    token = create_access_token(42)
    forged = token[:-3] + ("abc" if token[-3:] != "abc" else "xyz")
    with pytest.raises(jwt.InvalidTokenError):
        jwt.decode(forged, settings.secret_key, algorithms=[ALGORITHM])