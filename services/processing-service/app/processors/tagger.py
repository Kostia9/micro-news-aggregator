import re
from collections import Counter

TOPIC_KEYWORDS: dict[str, list[str]] = {
    "technology": [
        "ai",
        "algorithm",
        "android",
        "app",
        "apple",
        "artificial intelligence",
        "automation",
        "chip",
        "cloud",
        "computer",
        "cybersecurity",
        "data center",
        "developer",
        "device",
        "digital",
        "gpu",
        "hack",
        "hardware",
        "iphone",
        "llm",
        "machine learning",
        "microsoft",
        "model",
        "neural",
        "open source",
        "platform",
        "programming",
        "robot",
        "semiconductor",
        "software",
        "startup",
        "tech",
        "technology",
    ],
    "business": [
        "acquisition",
        "bank",
        "business",
        "ceo",
        "company",
        "corporate",
        "deal",
        "economy",
        "finance",
        "funding",
        "gdp",
        "inflation",
        "investment",
        "investor",
        "ipo",
        "layoff",
        "market",
        "merger",
        "profit",
        "recession",
        "revenue",
        "share",
        "stock",
        "trade",
    ],
    "politics": [
        "administration",
        "bill",
        "campaign",
        "congress",
        "democrat",
        "diplomacy",
        "diplomatic",
        "election",
        "government",
        "law",
        "legislation",
        "minister",
        "parliament",
        "policy",
        "president",
        "prime minister",
        "republican",
        "sanction",
        "senate",
        "vote",
        "war",
        "military",
    ],
    "sports": [
        "athlete",
        "baseball",
        "basketball",
        "champion",
        "championship",
        "coach",
        "cup",
        "football",
        "goal",
        "league",
        "match",
        "nba",
        "nfl",
        "olympic",
        "player",
        "race",
        "score",
        "soccer",
        "sport",
        "team",
        "tennis",
        "tournament",
        "win",
    ],
    "science": [
        "biology",
        "chemistry",
        "climate",
        "discovery",
        "disease",
        "environment",
        "experiment",
        "health",
        "medicine",
        "moon",
        "nasa",
        "physics",
        "planet",
        "research",
        "researcher",
        "science",
        "scientist",
        "space",
        "study",
        "trial",
        "vaccine",
    ],
}

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")
_TITLE_WEIGHT = 3
_CONTENT_WEIGHT = 1
_PHRASE_BONUS = 2
_MIN_SCORE = 3
_MAX_TOPICS = 3

_KEYWORD_LEMMAS = {
    keyword
    for keywords in TOPIC_KEYWORDS.values()
    for keyword in keywords
    if " " not in keyword
}


def _lemma(token: str) -> str:
    token = token.lower()
    irregular = {
        "ate": "eat",
        "bought": "buy",
        "children": "child",
        "elections": "election",
        "elected": "elect",
        "feet": "foot",
        "geese": "goose",
        "indices": "index",
        "men": "man",
        "mice": "mouse",
        "people": "person",
        "ran": "run",
        "saw": "see",
        "teeth": "tooth",
        "women": "woman",
    }
    if token in irregular:
        return irregular[token]
    if len(token) > 5 and token.endswith("ies"):
        return f"{token[:-3]}y"
    if len(token) > 5 and token.endswith("ves"):
        return f"{token[:-3]}f"
    if len(token) > 5 and token.endswith("ing"):
        stem = token[:-3]
        if len(stem) > 2 and stem[-1] == stem[-2]:
            stem = stem[:-1]
        if f"{stem}e" in _KEYWORD_LEMMAS:
            return f"{stem}e"
        return stem
    if len(token) > 4 and token.endswith("ied"):
        return f"{token[:-3]}y"
    if len(token) > 4 and token.endswith("ed"):
        stem = token[:-2]
        if len(stem) > 2 and stem[-1] == stem[-2]:
            stem = stem[:-1]
        if f"{stem}e" in _KEYWORD_LEMMAS:
            return f"{stem}e"
        return stem
    if len(token) > 4 and token.endswith(("ches", "shes", "sses", "xes", "zzes")):
        return token[:-2]
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


def _token_counts(text: str) -> Counter[str]:
    return Counter(_lemma(match.group(0)) for match in _TOKEN_RE.finditer(text.lower()))


def _phrase_in_text(phrase: str, text: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(phrase.lower()) + r"(?![a-z0-9])"
    return re.search(pattern, text.lower()) is not None


def _score_keyword(
    keyword: str,
    title: str,
    content: str,
    title_counts: Counter[str],
    content_counts: Counter[str],
) -> int:
    if " " in keyword:
        score = 0
        if _phrase_in_text(keyword, title):
            score += _TITLE_WEIGHT + _PHRASE_BONUS
        if _phrase_in_text(keyword, content):
            score += _CONTENT_WEIGHT + _PHRASE_BONUS
        return score

    lemma = _lemma(keyword)
    return (
        title_counts[lemma] * _TITLE_WEIGHT
        + content_counts[lemma] * _CONTENT_WEIGHT
    )


def score_topics(article: dict) -> dict[str, int]:
    title = article.get("title", "")
    content = article.get("content", "")
    title_counts = _token_counts(title)
    content_counts = _token_counts(content)

    scores: dict[str, int] = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(
            _score_keyword(keyword, title, content, title_counts, content_counts)
            for keyword in keywords
        )
        if score >= _MIN_SCORE:
            scores[topic] = score
    return scores


async def assign_topics(article: dict) -> list[str]:
    scores = score_topics(article)
    if not scores:
        return ["general"]
    ranked_topics = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return [
        topic
        for topic, _score in ranked_topics[:_MAX_TOPICS]
    ]
