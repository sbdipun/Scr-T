from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

# Create Flask app
app = Flask(__name__)

# ScraperAPI key and base URL
API_KEY = '8180f4dd3446354d073fe5e4203bd064'  # Replace with your actual ScraperAPI key
BASE_URL = 'https://www.1tamilmv.re/'

# ScraperAPI URL
SCRAPERAPI_URL = 'https://api.scraperapi.com/'

# Function to scrape the movie listing page using ScraperAPI
def tamilmv():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }
    results = []

    try:
        # Set up ScraperAPI request to fetch the main page
        params = {
            'api_key': API_KEY,
            'url': BASE_URL
        }
        response = requests.get(SCRAPERAPI_URL, headers=headers, params=params)
        response.raise_for_status()  # Raise an error if the request fails
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <li> elements that hold the movie links
        li_elements = soup.find_all('li', class_='ipsDataItem')

        if not li_elements:
            return [{"error": "No movie listings found. The page structure might have changed."}]

        # Extract the URLs for each topic (movie)
        topic_urls = [li.find('a', class_='ipsDataItem_title')['href'] for li in li_elements if li.find('a', class_='ipsDataItem_title')]

        # Scrape each topic URL for torrent details
        for topic_url in topic_urls:
            movie_details = get_movie_details(topic_url)
            results.append(movie_details)

    except requests.exceptions.RequestException as e:
        results = [{"error": str(e)}]

    return results

# Function to get details for each movie using ScraperAPI
def get_movie_details(url):
    movie_details = []

    try:
        # Set up ScraperAPI request to fetch the topic page
        params = {
            'api_key': API_KEY,
            'url': url
        }
        topic_response = requests.get(SCRAPERAPI_URL, params=params)
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
