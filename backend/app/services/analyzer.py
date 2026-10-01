import re


KYRGYZ_VOWELS = set("аоуыэиеөүёюя")

def count_syllables_in_word(word: str) -> int:

    word = word.lower()
    syllable_count = 0
    previous_was_vowel = False

    for char in word:
        is_vowel = char in KYRGYZ_VOWELS
        
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel

    return syllable_count


def split_into_words(text: str)-> list[str]:

    word = re.findall(r"[а-яА-ЯөүӨҮңҢёЁa-zA-Z]+", text)
    return word


def split_into_sentences(text: str)-> list[str]:

    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences


def analyze_text(text: str)-> dict:
    words = split_into_words(text)
    sentences = split_into_sentences(text)

    words_count = len(words)
    sentences_count = len(sentences)
    characters_count = sum(len(word) for word in words)

    if words_count == 0 or sentences_count == 0:
        return {"error": "Text has no valid words or sentences"}

    avg_characters_per_word = characters_count / words_count
    avg_words_per_sentence = words_count / sentences_count

    ari_score = (4.71 * avg_characters_per_word) + (0.5 * avg_words_per_sentence) - 21.43

    return {
        "words_count": words_count,
        "sentences_count": sentences_count,
        "characters_count": characters_count,
        "avg_characters_per_word": round(avg_characters_per_word, 2),
        "avg_words_per_sentence": round(avg_words_per_sentence, 2),
        "ari_score": round(ari_score, 2),
    }


def analyze_kyrgyz_readability(text: str)-> dict:

    words = split_into_words(text)
    sentences = split_into_sentences(text)

    words_count = len(words)
    sentences_count = len(sentences)

    if words_count == 0 or sentences_count == 0:
        return {"error": "Text has no valid words or sentences"}

    total_syllables = sum(count_syllables_in_word(word) for word in words)

    avg_syllables_per_word = total_syllables / words_count
    avg_words_per_sentence = words_count / sentences_count

    readability_score = 198.825 - (40.175 * avg_syllables_per_word) - (2.610 * avg_words_per_sentence)

    return{
        "words_count": words_count,
        "sentences_count": sentences_count,
        "total_syllables": total_syllables,
        "avg_syllables_per_word": round(avg_syllables_per_word, 2),
        "avg_words_per_sentence": round(avg_words_per_sentence, 2),
        "readability_score": round(readability_score, 2)
    }
