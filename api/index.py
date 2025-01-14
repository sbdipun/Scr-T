from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Custom headers for the requests
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

# Function to fetch the topic URLs from the main page
def fetch_topic_urls():
    BASE_URL = 'https://www.1tamilmv.re/'
    response = requests.get(BASE_URL, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    print("Page fetched successfully.")

    # Log the first 500 characters of the page content for debugging
    print(response.text[:500])

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Log the title to check if we're parsing the correct page
    print(f"Page Title: {soup.title.string}")

    # Check for the <li> elements again
    li_elements = soup.find_all('li', class_='ipsDataItem')
    print(f"Found {len(li_elements)} topic elements.")

    # Extract all topic URLs and store them in a list
    topic_urls = []
    for li in li_elements:
        topic_link = li.find('a', class_='ipsDataItem_title')
        if topic_link:
            topic_urls.append(topic_link['href'])

    return topic_urls

# Route to fetch movies (topic URLs)
@app.route("/movies", methods=["GET"])
def get_movies():
    topic_urls = fetch_topic_urls()

    if not topic_urls:
        return jsonify({"error": "No movie listings found. The page structure might have changed."}), 404

    return jsonify({"movies": topic_urls})


if __name__ == "__main__":
    app.run(debug=True)
