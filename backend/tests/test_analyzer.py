from app.services.analyzer import split_into_words, analyze_text


def test_split_into_words_handles_ng():
    assert split_into_words("Таңкы мектепке барам") == ["Таңкы", "мектепке", "барам"]


def test_split_into_words_handles_oe_ue():
    assert split_into_words("Өзүм көрдүм") == ["Өзүм", "көрдүм"]

def test_analyze_text_returns_expected_keys():
    result = analyze_text("Таңкы мектепке барам.")

    assert result["words_count"] == 3
    assert "ari_score" in result