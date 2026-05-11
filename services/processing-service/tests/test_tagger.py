import asyncio

from app.processors.tagger import _lemma, assign_topics, score_topics


def test_assign_topics_scores_title_higher_than_content() -> None:
    article = {
        "title": "AI chip startup raises new funding",
        "content": "The company said investors expect revenue growth.",
    }

    scores = score_topics(article)
    topics = asyncio.run(assign_topics(article))

    assert scores["technology"] > scores["business"]
    assert topics[:2] == ["technology", "business"]


def test_assign_topics_uses_lemmas_instead_of_exact_words() -> None:
    article = {
        "title": "Scientists studied vaccines in climate trials",
        "content": "Researchers published discoveries about diseases.",
    }

    assert asyncio.run(assign_topics(article)) == ["science"]


def test_assign_topics_avoids_substring_matches() -> None:
    article = {
        "title": "Chair repaired after rain",
        "content": "The story mentions plain words that should not match AI.",
    }

    assert asyncio.run(assign_topics(article)) == ["general"]


def test_assign_topics_limits_low_signal_single_content_keyword() -> None:
    article = {
        "title": "Local update",
        "content": "The report briefly mentioned the market.",
    }

    assert asyncio.run(assign_topics(article)) == ["general"]


def test_assign_topics_detects_phrase_keywords() -> None:
    article = {
        "title": "Prime minister announces election bill",
        "content": "The government said the new law will go to parliament.",
    }

    assert asyncio.run(assign_topics(article)) == ["politics"]


def test_lemma_keeps_silent_e_when_removing_plural_s() -> None:
    assert _lemma("devices") == "device"
    assert _lemma("shares") == "share"
    assert _lemma("trades") == "trade"
    assert _lemma("votes") == "vote"
    assert _lemma("races") == "race"
    assert _lemma("scores") == "score"
    assert _lemma("diseases") == "disease"
    assert _lemma("sciences") == "science"
    assert _lemma("spaces") == "space"
    assert _lemma("vaccines") == "vaccine"


def test_lemma_removes_es_for_sibilant_plurals() -> None:
    assert _lemma("boxes") == "box"
    assert _lemma("wishes") == "wish"
    assert _lemma("matches") == "match"
    assert _lemma("classes") == "class"


def test_lemma_restores_silent_e_for_ed_forms() -> None:
    assert _lemma("voted") == "vote"
    assert _lemma("traded") == "trade"
    assert _lemma("scored") == "score"
    assert _lemma("raced") == "race"
    assert _lemma("studied") == "study"
