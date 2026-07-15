"""RSS sample for investment fetch unit tests (no network)."""

SAMPLE_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Google News</title>
    <item>
      <title>Markets climb on earnings</title>
      <link>https://example.com/a</link>
      <description>&lt;a href="https://example.com/a"&gt;Markets climb&lt;/a&gt;</description>
    </item>
    <item>
      <title>Fed holds rates</title>
      <link>https://example.com/b</link>
      <description>Federal Reserve holds steady</description>
    </item>
    <item>
      <title>Tech slides</title>
      <link>https://example.com/c</link>
      <description>Megacap tech lower</description>
    </item>
    <item>
      <title>Should be ignored past limit</title>
      <link>https://example.com/d</link>
      <description>extra</description>
    </item>
  </channel>
</rss>
"""

TRUNCATED_RSS = SAMPLE_RSS[:80]
