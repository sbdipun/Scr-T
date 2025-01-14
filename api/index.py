from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Define headers to mimic a real browser request
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.6',
    'Cache-Control': 'max-age=0',
    'Cookie': 'ips4_ipsTimezone=Asia/Calcutta; ips4_hasJS=true; ips4_IPSSessionFront=o6tqf6g5mqq1dsmbip2spoa9a8',
    'If-Modified-Since': 'Tue, 14 Jan 2025 06:55:19 GMT',
    'Priority': 'u=0, i',
    'Referer': 'https://www.1tamilmv.re/',
    'Sec-CH-UA': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-GPC': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

# Function to scrape movies from 1tamilmv
def fetch_movies():
    BASE_URL = 'https://www.1tamilmv.re/'

    # Make a request to the website using the custom headers
    response = requests.get(BASE_URL, headers=headers)

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all <li> elements with the class 'ipsDataItem' (all topics)
    li_elements = soup.find_all('li', class_='ipsDataItem')

    # Extract all movie details (title and magnet links)
    movie_details = []

    for li in li_elements:
        topic_link = li.find('a', class_='ipsDataItem_title')
        if topic_link:
            topic_url = topic_link['href']

            # Make a request to the topic URL using the custom headers
            topic_response = requests.get(topic_url, headers=headers)
            topic_soup = BeautifulSoup(topic_response.text, 'html.parser')

            # Find all <a> elements with data-fileext="torrent" (magnet links)
            torrent_links = topic_soup.find_all('a', attrs={'data-fileext': 'torrent'})

            # Extract the torrent link and the file name/title from the <span> tag
            for torrent_link in torrent_links:
                magnet_link = torrent_link['href']
                
                # Extract title (from the <span> tag inside the <a> tag)
                title = torrent_link.find('span')
                if title:
                    title_text = title.get_text(strip=True)
                    
                    # Remove ".torrent" from the title if it exists
                    title_text = title_text.replace('.torrent', '').strip()

                    # Add the movie title and magnet link to the movie details list
                    movie_details.append({
                        'Title': title_text,
                        'Magnet Link': magnet_link
                    })

    return movie_details


# Define route for fetching movies
@app.route("/rss", methods=["GET"])
def rss():
    movies = fetch_movies()
    if movies:
        return jsonify({"movies": movies})
    else:
        return jsonify({"error": "No movies found."}), 404


# Define the home route
@app.route("/", methods=["GET"])
def home():
    return "Welcome to the Movie Scraper API!"


if __name__ == "__main__":
    app.run(debug=True)
