from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

# Create Flask app
app = Flask(__name__)

# Base URL
BASE_URL = 'https://www.1tamilmv.re'

# Function to scrape movie details
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


# Function to get movie details
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


# Define routes
@app.route("/")
def home():
    return jsonify({"message": "Welcome to TamilMV RSS FEED Site. Use /rss endpoint and Boom!! Developed by Mr. Shaw"})


# Route to return JSON feed
@app.route("/rss", methods=["GET"])
def fetch_movies():
    movie_list, movie_details = tamilmv()

    # Prepare the JSON output
    result = {
        "site_name": "TamilMV Latest Movies",
        "site_url": BASE_URL,
        "movies": []
    }

    for title, details in movie_details.items():
        for detail in details:
            result["movies"].append({
                "title": detail["title"],
                "size": detail["size"],
                "magnet_link": detail["magnet_link"],
                "torrent_file_link": detail["torrent_file_link"]
            })

    return jsonify(result)


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
