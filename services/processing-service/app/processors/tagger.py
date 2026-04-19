TOPIC_KEYWORDS: dict[str, list[str]] = {
    "technology": [
        "tech", "software", "hardware", "ai", "artificial intelligence",
        "machine learning", "deep learning", "neural", "robot", "automation",
        "startup", "cloud", "cybersecurity", "hack", "chip", "semiconductor",
        "smartphone", "computer", "programming", "developer", "open source",
        "algorithm", "model", "gpu", "llm",
    ],
    "business": [
        "business", "economy", "market", "stock", "finance", "investment",
        "bank", "revenue", "profit", "ipo", "merger", "acquisition",
        "ceo", "corporate", "trade", "gdp", "inflation", "recession",
    ],
    "politics": [
        "politics", "government", "election", "president", "congress", "senate",
        "parliament", "minister", "democrat", "republican", "vote", "policy",
        "legislation", "diplomatic", "sanctions", "war", "military",
    ],
    "sports": [
        "sport", "football", "soccer", "basketball", "tennis", "olympic",
        "athlete", "championship", "tournament", "league", "team", "coach",
        "match", "goal", "score",
    ],
    "science": [
        "science", "research", "study", "nasa", "space", "climate",
        "environment", "health", "medicine", "vaccine", "biology", "physics",
        "chemistry", "discovery", "experiment",
    ],
}


async def assign_topics(article: dict) -> list[str]:
    text = (article.get("title", "") + " " + article.get("content", "")).lower()
    matched = [
        topic
        for topic, keywords in TOPIC_KEYWORDS.items()
        if any(kw in text for kw in keywords)
    ]
    return matched if matched else ["general"]
