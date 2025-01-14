from flask import Flask, jsonify, Response
import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
import re

# Initialize Flask app
app = Flask(__name__)

# Base URL to scrape
base_url = "https://www.1tamilblasters.party/"

# Headers for requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

# Function to scrape the latest links and magnet links
def scrape_links():
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all('div', class_='ipsType_break ipsContained')

        # Limit to 10 links to prevent timeout
        links = [div.find('a')['href'] for div in divs[:10] if div.find('a')]

        results = []
        for link in links:
            sub_response = requests.get(link, headers=headers, timeout=10)
            sub_response.raise_for_status()

            sub_soup = BeautifulSoup(sub_response.text, 'html.parser')
            magnet_link_tag = sub_soup.find('a', class_='magnet-plugin')

            if magnet_link_tag and 'href' in magnet_link_tag.attrs:
                magnet_link = magnet_link_tag['href']
                query_params = parse_qs(urlparse(magnet_link).query)
                title = query_params.get('dn', ['No Title'])[0]

                # Extract size from the title (e.g., "Movie Title (Size: 1.5 GB)")
                size_match = re.search(r'\(([^)]+)\)', title)
                size = size_match.group(1) if size_match else 'Unknown Size'

                description = f"Size: {size}, mag link: {magnet_link}"
                results.append({"title": title, "magnet_link": magnet_link, "description": description, "size": size})
        return results
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []

# Home Route - Returns JSON
@app.route('/')
def home():
    data = scrape_links()
    return jsonify(data)

# RSS Route - Returns XML
@app.route("/")
def home():   
    return jsonify({"message": "Welcome to TamilBlasters RSS FEED Site. Use /rss end of the Url and BooM!! Developed By Mr. Shaw"})

    # Build the RSS XML feed
    rss_items = ""
    for item in data:
        rss_items += f"""
            <item>
                <title>{item['title']}</title>
                <link>{item['magnet_link']}</link>
                <description>{item['description']}</description>
            </item>
        """

    rss_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>Tamil Blasters RSS Feed</title>
                <link>{base_url}</link>
                <description>Latest Movies and TV Shows</description>
                {rss_items}
            </channel>
        </rss>
    """

    return Response(rss_feed, mimetype='application/rss+xml')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
