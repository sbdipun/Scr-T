from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Define a function to get the movie details from the given link
def get_movie_details(movie_url):
    # Send GET request with headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }
    
    # Fetch the movie page content
    response = requests.get(movie_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    
    # You can extract specific movie details here (for example, genre, release date, etc.)
    # Adjust according to the actual page structure
    details = soup.find_all('div', {'class': 'some_detail_class'})  # Change this to actual class or tag
    
    # Extract relevant details from the page (example)
    movie_details = {}
    for detail in details:
        # Assuming the details are stored in some structured way
        detail_title = detail.find('span', {'class': 'some_class'}).text.strip()  # Adjust based on actual content
        movie_details[detail_title] = detail.text.strip()
    
    return movie_details

# Define a function to scrape movie listings
def scrape_movies():
    mainUrl = 'https://www.1tamilmv.re/'  # Replace with the actual URL

    # Send GET request with headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }
    
    # Initialize movie list and details dictionary
    movie_list = []
    real_dict = {}
    
    # Request the main page
    web = requests.get(mainUrl, headers=headers)
    soup = BeautifulSoup(web.text, 'lxml')

    # Find the movie elements (adjust the class based on actual structure)
    temps = soup.find_all('div', {'class': 'ipsType_break ipsContained'})
    
    # If there are less than 21 movie entries, return empty
    if len(temps) < 21:
        return [], {}

    # Iterate through the movie elements and extract titles and links
    for i in range(21):
        title = temps[i].find_all('a')[0].text.strip()  # Get the movie title
        link = temps[i].find('a')['href']  # Get the movie link
        movie_list.append(title)
        
        # Get the details for each movie
        movie_details = get_movie_details(link)
        real_dict[title] = movie_details

    return movie_list, real_dict

# Define the route to get the movie listings
@app.route('/movies', methods=['GET'])
def get_movies():
    movie_list, real_dict = scrape_movies()
    
    # Check if any movies were found
    if movie_list:
        return jsonify({'movies': movie_list, 'movie_details': real_dict})
    else:
        return jsonify({'error': 'No movies found.'}), 404

# Define the home route
@app.route('/')
def home():
    return 'Welcome to the Movie Scraper API!'

if __name__ == '__main__':
    app.run(debug=True)
