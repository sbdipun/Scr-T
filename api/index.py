from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to scrape movie details
def fetch_movies():
    url = "https://www.1tamilmv.re/"  # Change this if necessary

    # Send a request to the website
    response = requests.get(url)

    # Use lxml parser with BeautifulSoup
    soup = BeautifulSoup(response.text, 'lxml')

    # Debugging: Print the first part of the raw HTML to inspect the structure
    print(soup.prettify()[:1000])  # Prints first 1000 characters of prettified HTML

    # Find all <li> elements with the class 'ipsDataItem' (all topics)
    li_elements = soup.find_all('li', class_='ipsDataItem')

    # Debugging: Check how many topics were found
    print(f"Found {len(li_elements)} topic elements.")
    
    topic_urls = []
    for li in li_elements:
        topic_link = li.find('a', class_='ipsDataItem_title')
        if topic_link:
            topic_urls.append(topic_link['href'])
    
    print(f"Found {len(topic_urls)} topic URLs.")

    results = []

    # Scrape each topic URL one by one
    for topic_url in topic_urls:
        topic_response = requests.get(topic_url)
        topic_soup = BeautifulSoup(topic_response.text, 'lxml')

        # Find all <a> elements with data-fileext="torrent" (magnet links)
        torrent_links = topic_soup.find_all('a', attrs={'data-fileext': 'torrent'})

        for torrent_link in torrent_links:
            magnet_link = torrent_link['href']
            title = torrent_link.find('span')
            if title:
                title_text = title.get_text(strip=True)
                title_text = title_text.replace('.torrent', '').strip()

                results.append({
                    'Title': title_text,
                    'Magnet Link': magnet_link
                })

    return results


@app.route("/")
def home():
    return "Welcome to the Tamil Movie Scraper API!"

@app.route("/rss", methods=["GET"])
def get_movies():
    try:
        # Fetch movies
        movies = fetch_movies()
        
        # Debugging: Log the HTML content to see if we're scraping correctly
        print(movies)
        
        if not movies:
            return jsonify({"error": "No movies found."}), 404
        return jsonify({"movies": movies})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
