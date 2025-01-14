from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Create Flask app
app = Flask(__name__)

# Base URL of the website to scrape
BASE_URL = 'https://www.1tamilmv.re/'

# Function to scrape movies
def tamilmv():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }
    movie_list = []
    real_dict = {}

    try:
        # Make the request to the main URL
        response = requests.get(BASE_URL, headers=headers, timeout=10)
        response.raise_for_status()  # Check for request errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # Scrape movie titles and links
        li_elements = soup.find_all('li', class_='ipsDataItem')
        topic_urls = [urljoin(BASE_URL, li.find('a', class_='ipsDataItem_title')['href']) for li in li_elements]

        # Iterate over each topic URL to get details
        for topic_url in topic_urls:
            topic_details = get_movie_details(topic_url)
            movie_list.append(topic_url)
            real_dict[topic_url] = topic_details

    except requests.exceptions.RequestException as e:
        return [], {"error": str(e)}

    return movie_list, real_dict

# Function to get movie details
def get_movie_details(url):
    try:
        # Fetch the movie detail page
        topic_response = requests.get(url, timeout=10)
        topic_response.raise_for_status()  # Check for request errors
        topic_soup = BeautifulSoup(topic_response.text, 'html.parser')

        # Find all magnet links
        torrent_links = topic_soup.find_all('a', attrs={'data-fileext': 'torrent'})
        movie_details = []

        for torrent_link in torrent_links:
            magnet_link = torrent_link['href']
            
            # Extract the title from the <span> tag and remove ".torrent"
            title_tag = torrent_link.find('span')
            if title_tag:
                title = title_tag.get_text(strip=True).replace('.torrent', '').strip()

                movie_details.append({
                    'title': title,
                    'magnet_link': magnet_link
                })

        return movie_details
    except Exception as e:
        return {"error": str(e)}

# Define routes
@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Movie Scraper API!"})

@app.route("/rss", methods=["GET"])
def fetch_movies():
    movie_list, movie_details = tamilmv()
    return jsonify({
        "movies": movie_list,
        "details": movie_details
    })

# Expose the app as `app`
if __name__ == "__main__":
    app.run(debug=True)
