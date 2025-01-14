from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Create Flask app
app = Flask(__name__)

# Base URL of the target website
BASE_URL = 'https://www.1tamilmv.re/'

# Function to scrape the movie listing page and get the movie details
def tamilmv():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }
    movie_details = []

    try:
        # Fetch the main page
        response = requests.get(BASE_URL, headers=headers)
        response.raise_for_status()  # Raise an error if the request fails
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <li> elements that hold the movie links
        li_elements = soup.find_all('li', class_='ipsDataItem')

        if not li_elements:
            return [{"error": "No movie listings found. The page structure might have changed."}]

        # For each <li>, scrape the topic URL and get movie details
        for li in li_elements:
            movie_title = li.find('a', class_='ipsDataItem_title').text.strip()
            topic_url = li.find('a', class_='ipsDataItem_title')['href']

            # Now, get the movie details for each topic URL
            details = get_movie_details(topic_url)
            movie_details.extend(details)

    except requests.exceptions.RequestException as e:
        movie_details = [{"error": str(e)}]

    return movie_details

# Function to get details for each movie by scraping the topic URL
def get_movie_details(url):
    movie_details = []

    try:
        # Make a request to the topic URL
        full_url = urljoin(BASE_URL, url)  # Ensure we use an absolute URL
        topic_response = requests.get(full_url)
        topic_response.raise_for_status()  # Raise an error if the request fails
        topic_soup = BeautifulSoup(topic_response.text, 'html.parser')

        # Find all torrent links (magnet links)
        torrent_links = topic_soup.find_all('a', attrs={'data-fileext': 'torrent'})

        for torrent_link in torrent_links:
            magnet_link = torrent_link['href']
            
            # Extract the title from the <span> inside the <a> tag
            title_tag = torrent_link.find('span')
            if title_tag:
                title = title_tag.get_text(strip=True).replace('.torrent', '').strip()

                # Add the movie details to the list
                movie_details.append({
                    'title': title,
                    'magnet_link': magnet_link
                })
    except Exception as e:
        movie_details = [{"error": str(e)}]

    return movie_details

# Home route for the Flask API
@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Movie Scraper API!"})

# RSS route for the Flask API to fetch movie data
@app.route("/rss", methods=["GET"])
def fetch_movies():
    movies = tamilmv()
    return jsonify({"movies": movies})

# Expose the app to run
if __name__ == "__main__":
    app.run(debug=True)
