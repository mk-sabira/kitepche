from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.origin import add_origin_check

ALLOWED = ["https://app.example.com"]


def make_client():
    app = FastAPI()
    add_origin_check(app, ALLOWED)

    @app.get("/thing")
    def read_thing():
        return {"ok": True}

    @app.post("/thing")
    def create_thing():
        return {"ok": True}

    @app.delete("/thing")
    def delete_thing():
        return {"ok": True}

    return TestClient(app)


def test_post_from_an_allowed_origin_works():
    client = make_client()
    response = client.post("/thing", headers={"Origin": "https://app.example.com"})
    assert response.status_code == 200


def test_post_from_a_foreign_origin_is_refused():
    client = make_client()
    response = client.post("/thing", headers={"Origin": "https://evil.example.com"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Origin not allowed"


def test_delete_from_a_foreign_origin_is_refused():
    client = make_client()
    response = client.delete("/thing", headers={"Origin": "https://evil.example.com"})
    assert response.status_code == 403


def test_post_with_a_null_origin_is_refused():
    client = make_client()
    assert client.post("/thing", headers={"Origin": "null"}).status_code == 403


def test_post_without_an_origin_header_works():
    # curl, scripts and tests send no Origin; the risk comes from browsers
    client = make_client()
    assert client.post("/thing").status_code == 200


def test_reading_from_a_foreign_origin_is_not_blocked_by_this_check():
    client = make_client()
    response = client.get("/thing", headers={"Origin": "https://evil.example.com"})
    assert response.status_code == 200
    