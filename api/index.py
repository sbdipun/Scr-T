from flask import Flask, jsonify
import requests
from lxml import html

app = Flask(__name__)

# Define a function to scrape the required content
def scrape_movies():
    url = 'https://www.1tamilmv.re/'  # Replace with the actual URL

    # Send GET request
    response = requests.get(url)

    # Parse the page content using lxml
    tree = html.fromstring(response.content)

    # Find all <div> tags with the class 'ipsType_break ipsContained'
    div_elements = tree.xpath("//div[@class='ipsType_break ipsContained']")

    # Extract and return the content inside those <div> tags
    movies = []
    for div in div_elements:
        movie_title = div.text_content().strip()  # Get the clean text inside the <div>
        if movie_title:  # Only add non-empty titles
            movies.append(movie_title)

    return movies

# Define the route for the home page
@app.route('/')
def home():
    return 'Welcome to the Movie Scraper API!'

# Define the route to get the movies
@app.route('/movies', methods=['GET'])
def get_movies():
    movies = scrape_movies()
    if movies:
        return jsonify({'movies': movies})
    else:
        return jsonify({'error': 'No movies found.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
