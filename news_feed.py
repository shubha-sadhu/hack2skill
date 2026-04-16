import feedparser

url = "https://news.google.com/rss/search?q=supply+chain+disruption+OR+logistics+delay+when:1d"

feed = feedparser.parse(url)

for entry in feed.entries:
    print(entry.title)