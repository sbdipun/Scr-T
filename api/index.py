from flask import Flask, Response, jsonify
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

# Create Flask app
app = Flask(__name__)

# Base URL
BASE_URL = 'https://www.1tamilmv.app/index.php'

# Function to scrape movie details
def tamilmv():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    real_list = []
    web = requests.get(BASE_URL, headers=headers)
    soup = BeautifulSoup(web.text, 'lxml')

    # Find all the movie elements
    temps = soup.find_all('div', {'class': 'ipsType_break ipsContained'})

    # Extract movie details in reverse order to get the latest on top
    for temp in reversed(temps):
        title = temp.find('a').text.strip()
        link = temp.find('a')['href']
        movie_details = get_movie_details(link)
        real_list.append({"title": title, "details": movie_details})

    return real_list

# Function to get movie details
def get_movie_details(url):
    try:
        if not url.startswith(('http://', 'https://')):
            url = urllib.parse.urljoin(BASE_URL, url)

        html = requests.get(url, timeout=10)
        html.raise_for_status()
        soup = BeautifulSoup(html.text, 'lxml')

        mag = [a['href'] for a in soup.find_all('a', href=True) if 'magnet:' in a['href']]
        filelink = [a['href'] for a in soup.find_all('a', {"data-fileext": "torrent", 'href': True})]

        movie_title = soup.find('h1').text.strip() if soup.find('h1') else "Unknown Title"

        movie_details = []
        for p in range(len(mag)):
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(mag[p]).query)
            if 'dn' in query_params:
                title_encoded = query_params['dn'][0]
                movie_title = urllib.parse.unquote(title_encoded)

                # Extract size from the dn parameter
                size_match = re.search(r'(\d+(\.\d+)?\s?(GB|MB|TB))', movie_title)
                size = size_match.group(1) if size_match else "Unknown"

            movie_details.append({
                "title": movie_title,
                "size": size,
                "magnet_link": mag[p],
                "torrent_file_link": filelink[p] if p < len(filelink) else None
            })

        return movie_details
    except Exception as e:
        return {"error": str(e)}

# Define routes
@app.route("/")
def home():   
    return jsonify({"message": "Welcome to TamilMV RSS FEED Site. Use /rss end of the Url and BooM!! Developed By Mr. Shaw"})

# Route to display RSS feed
@app.route("/rss", methods=["GET"])
def fetch_movies():
    movie_details = tamilmv()

    # Generate RSS XML
    rss_feed = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<rss version=\"2.0\">
<channel>
    <title>TamilMV Latest Movies</title>
    <link>{base_url}</link>
    <description>Latest movies from TamilMV!! Made By Mr. Shaw</description>
""".format(base_url=BASE_URL)

    for movie in movie_details:
        for detail in movie["details"]:
            rss_feed += f"""
    <item>
        <title>{detail['title']}</title>
        <link>{detail['magnet_link']}</link>
        <description>Size: {detail['size']}, Torrent File: {detail['torrent_file_link']}</description>
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
