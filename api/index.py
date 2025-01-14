from flask import Flask, Response, jsonify
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

# Create Flask app
app = Flask(__name__)

# Base URL
BASE_URL = 'https://www.1tamilmv.re'

def tamilmv():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    movie_list = []
    real_dict = {}

    web = requests.get(BASE_URL, headers=headers)
    soup = BeautifulSoup(web.text, 'lxml')

    temps = soup.find_all('div', {'class': 'ipsType_break ipsContained'})

    if len(temps) < 21:
        return [], {}

    for i in range(21):
        title = temps[i].findAll('a')[0].text.strip()
        link = temps[i].find('a')['href']
        movie_list.append(title)

        movie_details = get_movie_details(link)
        real_dict[title] = movie_details

    return movie_list, real_dict


def get_movie_details(url):
    try:
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'lxml')

        mag = [a['href'] for a in soup.find_all('a', href=True) if 'magnet:' in a['href']]
        filelink = [a['href'] for a in soup.find_all('a', {"data-fileext": "torrent", 'href': True})]

        movie_details = []
        movie_title = soup.find('h1').text.strip() if soup.find('h1') else "Unknown Title"

        for p in range(len(mag)):
            # Extract size from the dn parameter in the magnet link
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(mag[p]).query)
            size = "Unknown"
            if 'dn' in query_params:
                title_encoded = query_params['dn'][0]
                movie_title = urllib.parse.unquote(title_encoded)

                # Use regex to extract size (e.g., 2.7GB or 700MB)
                size_match = re.search(r'(\d+(\.\d+)?\s?(GB|MB|TB))', movie_title)
                if size_match:
                    size = size_match.group(1)

            movie_details.append({
                "title": movie_title,
                "size": size,
                "magnet_link": mag[p],
                "torrent_file_link": filelink[p] if p < len(filelink) else None
            })

        return movie_details
    except Exception as e:
        return {"error": str(e)}


# Function to escape special characters in URLs (like & to &amp;)
def escape_xml(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

# Define routes
@app.route("/")
def home():   
    return jsonify({"message": "Welcome to TamilMV RSS FEED Site. Use /rss end of the Url and BooM!! Developed By Mr. Shaw"})

# Route to display RSS feed
@app.route("/rss", methods=["GET"])
def fetch_movies():
    movie_details = tamilmv()

    # Generate RSS XML
    rss_feed = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>TamilMV Latest Movies</title>
    <link>{base_url}</link>
    <description>Latest movies from TamilMV!! Developed By Mr. Shaw</description>
""".format(base_url=BASE_URL)

    for movie in movie_details:
        for detail in movie["details"]:
            rss_feed += f"""
    <item>
        <title>{escape_xml(detail['title'])}</title>
        <link>{escape_xml(detail['magnet_link'])}</link>
        <description>Size: {escape_xml(detail['size'])}, Torrent File: {escape_xml(detail['torrent_file_link'])}</description>
    </item>
"""

    rss_feed += """
</channel>
</rss>
"""

    return Response(rss_feed, mimetype='application/rss+xml')

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)

    
