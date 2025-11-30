from curl_cffi import requests
from bs4 import BeautifulSoup
from flask import Flask, Response, jsonify

app = Flask(__name__)

BASE = "https://uindex.org"

URLS = [
    "https://uindex.org/search.php?c=1",
    "https://uindex.org/search.php?c=2"
]


def scrape(url):
    try:
        resp = requests.get(url, impersonate="chrome")
    except Exception as e:
        print("Request failed:", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []

    rows = soup.select("tbody tr")[:10]  # get only 10 per category

    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 3:
            continue

        name_td = tds[1]
        size_td = tds[2]

        # find proper title link
        title_link = None
        for a in name_td.find_all("a"):
            txt = a.get_text(strip=True)
            if txt:
                title_link = a
                break

        if not title_link:
            continue

        title = title_link.get_text(strip=True)
        href = title_link.get("href", "")
        if href.startswith("/"):
            href = BASE + href

        # magnet link
        magnet = None
        for a in name_td.find_all("a"):
            h = a.get("href", "")
            if h.startswith("magnet:?"):
                magnet = h
                break

        size = size_td.get_text(strip=True)

        items.append({
            "title": title,
            "link": href,
            "magnet": magnet,
            "size": size
        })

    return items

@app.route("/")
def home():   
    return jsonify({"message": "UIndex Rss Feed is Up and Running..."})
    
@app.route("/rss")
def rss_feed():
    all_items = []

    for url in URLS:
        all_items.extend(scrape(url))

    # Build RSS
    rss = '<?xml version="1.0" encoding="UTF-8"?>\n'
    rss += '<rss version="2.0"><channel>\n'
    rss += '<title>UIndex Torrent Feed</title>\n'
    rss += '<link>https://uindex.org</link>\n'
    rss += '<description>Latest torrents</description>\n'

    for item in all_items:
        rss += "<item>\n"
        rss += f"<title><![CDATA[{item['title']} | {item['size']}]]></title>\n"
        rss += f"<link>{item['link']}</link>\n"
        if item["magnet"]:
            rss += f"<magnet><![CDATA[{item['magnet']}]]></magnet>\n"
        rss += "</item>\n"

    rss += "</channel></rss>"

    return Response(rss, content_type="application/xml")
