from dataclasses import dataclass


@dataclass
class RawArticle:
    title: str
    url: str
    published_at: str
    content: str
    source: str


def parse_feed(raw_xml: bytes, source_name: str) -> list[RawArticle]:
    pass
