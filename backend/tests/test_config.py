from app.core.config import Settings


def make_settings(**overrides):
    values = {
        "database_url": "postgresql://x:x@localhost/x",
        "gemini_api_key": "x",
        "secret_key": "x",
    }
    values.update(overrides)
    return Settings(**values)


def test_cors_origins_are_split_and_trimmed():
    s = make_settings(cors_origins="https://a.com, https://b.com ,")

    assert s.cors_origin_list == ["https://a.com", "https://b.com"]


def test_cors_origins_single_value():
    s = make_settings(cors_origins="https://only.example.com")

    assert s.cors_origin_list == ["https://only.example.com"]
