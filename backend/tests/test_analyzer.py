from app.services.analyzer import split_into_words, analyze_text, find_difficult_words


def test_split_into_words_handles_ng():
    assert split_into_words("Таңкы мектепке барам") == ["Таңкы", "мектепке", "барам"]


def test_split_into_words_handles_oe_ue():
    assert split_into_words("Өзүм көрдүм") == ["Өзүм", "көрдүм"]

def test_analyze_text_returns_expected_keys():
    result = analyze_text("Таңкы мектепке барам.")

    assert result["words_count"] == 3
    assert "ari_score" in result


def test_find_difficult_words_puts_longest_first():
    result = find_difficult_words("Мен китеп окуймун. Мен мээримдүүлүккө барам.")
    words = [item["word"] for item in result["difficult_words"]]
    assert words[0] == "мээримдүүлүккө"


def test_find_difficult_words_has_no_duplicates():
    result = find_difficult_words("китеп китеп китеп")
    assert len(result["difficult_words"]) == 1


def test_find_difficult_words_handles_empty_text():
    assert find_difficult_words("") == {"error": "Text has no valid words"}