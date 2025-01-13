from flask import Flask, Response, request
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Create Flask app
app = Flask(__name__)

# Base URL
BASE_URL = 'https://www.1tamilmv.app/index.php'

# Function to scrape movie details
def tamilmv():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }
    
    real_dict = {}
    
    web = requests.get(BASE_URL, headers=headers)
    soup = BeautifulSoup(web.text, 'lxml')

    # Find all the movie elements
    temps = soup.find_all('div', {'class': 'ipsType_break ipsContained'})
    
    if len(temps) < 21:
        return {}

    # Reverse the list to get the latest posts on top
    temps = temps[::-1]

    for i in range(21):
        title = temps[i].findAll('a')[0].text.strip()
        link = temps[i].find('a')['href']
        
        movie_details = get_movie_details(link)
        real_dict[title] = movie_details

    return real_dict

# Function to get movie details
def get_movie_details(url):
    try:
        # Check if the URL starts with http:// or https://
        if not url.startswith(('http://', 'https://')):
            # Construct the full URL using the base URL
            url = urllib.parse.urljoin(BASE_URL, url)

        html = requests.get(url, timeout=10)
        html.raise_for_status()
        soup = BeautifulSoup(html.text, 'lxml')

        # Extract all magnet and torrent links
        mag = [a['href'] for a in soup.find_all('a', href=True) if 'magnet:' in a['href']]
        filelink = [a['href'] for a in soup.find_all('a', {"data-fileext": "torrent", 'href': True})]

        # Movie title extraction (from <h1> tag or 'dn' parameter in the magnet link)
        movie_title = soup.find('h1').text.strip() if soup.find('h1') else "Unknown Title"

        movie_details = []
        
        for p in range(len(mag)):
            # Parse the 'dn' parameter in the magnet link if available
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(mag[p]).query)
            if 'dn' in query_params:
                title_encoded = query_params['dn'][0]  # Get the first value of 'dn'
                movie_title = urllib.parse.unquote(title_encoded)  # Decode the URL-encoded title

            movie_details.append({
                "title": movie_title,
                "magnet_link": mag[p],
                "torrent_file_link": filelink[p] if p < len(filelink) else None
            })

        return movie_details
    except Exception as e:
        return {"error": str(e)}

# Define routes
@app.route("/")
def home():
    return jsonify({"message": "Welcome to TamilMV Scrapper Site!! Developed By Mr. Shaw"})

@app.route("/fetch", methods=["GET"])
def fetch_movies():
    # Get movie details
    movie_details = tamilmv()

    # Generate RSS XML
    rss_feed = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>TamilMV Latest Movies</title>
    <link>{base_url}</link>
    <description>Latest movies from TamilMV</description>
""".format(base_url=BASE_URL)

    for title, details in movie_details.items():
        for detail in details:
            rss_feed += f"""
    <item>
        <title>{detail['title']}</title>
        <link>{detail['magnet_link']}</link>
        <description>Download link: {detail['torrent_file_link']}</description>
    </item>
"""

    rss_feed += """
</channel>
</rss>
"""

    # Return the RSS feed as a response with the appropriate content type
    return Response(rss_feed, mimetype='application/rss+xml')

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
