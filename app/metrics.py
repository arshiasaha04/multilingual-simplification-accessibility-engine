import re
import unicodedata


_SENTENCE_PATTERN = re.compile(r"[.!?।॥]+")


def _word_count(text: str) -> int:
    count = 0
    in_word = False
    for character in text:
        category = unicodedata.category(character)
        if category[0] in {"L", "N"} or (
            in_word and (category[0] == "M" or category == "Cf")
        ):
            in_word = True
        elif in_word:
            count += 1
            in_word = False
    return count + int(in_word)


def _indic_character_count(text: str) -> int:
    count = 0
    for character in text:
        codepoint = ord(character)
        if (
            0x0900 <= codepoint <= 0x0DFF
            or 0x0F00 <= codepoint <= 0x109F
            or 0x1780 <= codepoint <= 0x17FF
            or 0xA800 <= codepoint <= 0xABFF
            or 0x11000 <= codepoint <= 0x11FFF
        ):
            if unicodedata.category(character).startswith("L"):
                count += 1
    return count


def readability_metrics(text: str) -> dict[str, float | int]:
    sentences = [part for part in _SENTENCE_PATTERN.split(text) if part.strip()]
    sentence_count = max(1, len(sentences)) if text.strip() else 0
    word_count = _word_count(text)
    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_words_per_sentence": round(word_count / sentence_count, 2)
        if sentence_count
        else 0.0,
        "indic_character_count": _indic_character_count(text),
    }


def back_translation_similarity(source: str, back_translation: str) -> float:
    """Estimate semantic retention with TF-IDF cosine similarity."""
    if not source.strip() or not back_translation.strip():
        return 0.0
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    matrix = TfidfVectorizer(analyzer="char", ngram_range=(2, 4)).fit_transform(
        [source, back_translation]
    )
    return round(float(cosine_similarity(matrix[0:1], matrix[1:2])[0, 0]), 4)
