import json, urllib.request, email.utils, datetime
import xml.etree.ElementTree as ET

FEEDS = [
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss"),
    ("Cointelegraph", "https://cointelegraph.com/rss"),
    ("Decrypt", "https://decrypt.co/feed"),
]
PER_FEED = 15

def parse_date(s):
    try:
        return email.utils.parsedate_to_datetime(s).astimezone(datetime.timezone.utc).isoformat()
    except Exception:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

items = []
for name, url in FEEDS:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (news-aggregator)"})
        with urllib.request.urlopen(req, timeout=20) as r:
            root = ET.fromstring(r.read())
        for it in root.iter("item"):
            title = (it.findtext("title") or "").strip()
            link = (it.findtext("link") or "").strip()
            if title and link.startswith("http"):
                items.append({"source": name, "title": title, "url": link,
                              "published": parse_date(it.findtext("pubDate") or "")})
                if sum(1 for x in items if x["source"] == name) >= PER_FEED:
                    break
    except Exception as e:
        print("feed failed:", name, e)

items.sort(key=lambda x: x["published"], reverse=True)
out = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(), "items": items[:60]}
if items:
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
print("saved", len(items), "items")
