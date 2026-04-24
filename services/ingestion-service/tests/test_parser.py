from app.parser.feed import parse_feed


def test_parse_feed_reads_rss_item_content_and_date() -> None:
    raw_xml = b"""
    <rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
      <channel>
        <title>Example Feed</title>
        <item>
          <title>RSS Story</title>
          <link>https://example.com/rss-story</link>
          <pubDate>Sun, 19 Apr 2026 12:30:00 GMT</pubDate>
          <description>Short description</description>
          <content:encoded>Full RSS content</content:encoded>
        </item>
      </channel>
    </rss>
    """

    articles = parse_feed(raw_xml, source_name="Example", source_topics=["general"])

    assert len(articles) == 1
    assert articles[0].title == "RSS Story"
    assert articles[0].url == "https://example.com/rss-story"
    assert articles[0].source == "Example"
    assert articles[0].topics == ["general"]
    assert articles[0].content == "Full RSS content"
    assert articles[0].published_at == "2026-04-19T12:30:00+00:00"


def test_parse_feed_reads_atom_entry_with_id_and_summary() -> None:
    raw_xml = b"""
    <feed xmlns="http://www.w3.org/2005/Atom">
      <title>Atom Feed</title>
      <entry>
        <title>Atom Story</title>
        <id>urn:article:1</id>
        <updated>2026-04-19T15:00:00Z</updated>
        <summary>Atom summary</summary>
      </entry>
    </feed>
    """

    articles = parse_feed(raw_xml, source_name="Atom Source", source_topics=["science"])

    assert len(articles) == 1
    assert articles[0].title == "Atom Story"
    assert articles[0].url == "urn:article:1"
    assert articles[0].topics == ["science"]
    assert articles[0].content == "Atom summary"
    assert articles[0].published_at == "2026-04-19T15:00:00+00:00"


def test_parse_feed_skips_entries_without_title_or_url() -> None:
    raw_xml = b"""
    <rss version="2.0">
      <channel>
        <item>
          <title>Missing URL</title>
          <description>Skipped</description>
        </item>
        <item>
          <link>https://example.com/missing-title</link>
          <description>Skipped</description>
        </item>
      </channel>
    </rss>
    """

    assert parse_feed(raw_xml, source_name="Example") == []


def test_parse_feed_falls_back_to_description() -> None:
    raw_xml = b"""
    <rss version="2.0">
      <channel>
        <item>
          <title>Description Story</title>
          <link>https://example.com/description-story</link>
          <description>Description fallback</description>
        </item>
      </channel>
    </rss>
    """

    articles = parse_feed(raw_xml, source_name="Example")

    assert len(articles) == 1
    assert articles[0].content == "Description fallback"
