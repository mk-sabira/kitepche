import unicodedata
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings

MAX_PASSWORD_BYTES = 72
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60
ACCESS_TOKEN_COOKIE = "access_token"

password_hash = PasswordHash((BcryptHasher(),))


def _prepare(password: str) -> str:
    return unicodedata.normalize("NFKC", password)


def _too_long(password: str) -> bool:
    return len(password.encode("utf-8")) > MAX_PASSWORD_BYTES


def hash_password(password: str) -> str:
    prepared = _prepare(password)
    if _too_long(prepared):
        raise ValueError("Password must be at most 72 bytes")
    return password_hash.hash(prepared)


def verify_password(password: str, hashed_password: str) -> bool:
    prepared = _prepare(password)
    if _too_long(prepared):
        return False
    return password_hash.verify(prepared, hashed_password)


# A fake hash for logins with an unknown email, so rejecting them takes as long
# as rejecting a wrong password
DUMMY_HASH = password_hash.hash("dummypassword")

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError):
        return None
