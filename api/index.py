from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Add headers to mimic a real browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

def fetch_topic_urls():
    BASE_URL = 'https://www.1tamilmv.re/'
    
    try:
        response = requests.get(BASE_URL, headers=headers)

        # Check if page was fetched successfully
        if response.status_code != 200:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return []

        print("Page fetched successfully.")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <li> elements with the class 'ipsDataItem' that contain movie topics
        li_elements = soup.find_all('li', class_='ipsDataItem')
        print(f"Found {len(li_elements)} topic elements.")

        topic_urls = []
        for li in li_elements:
            # Extract the <a> tag with class 'ipsDataItem_title' inside each <li> item
            topic_link = li.find('a', class_='ipsDataItem_title')
            if topic_link:
                topic_urls.append(topic_link['href'])

        return topic_urls

    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return []

@app.route("/movies", methods=["GET"])
def fetch_movies():
    # Fetch the topic URLs
    topic_urls = fetch_topic_urls()
    
    # If no URLs found, return an error message
    if not topic_urls:
        return jsonify({"error": "No movie listings found. The page structure might have changed."}), 404

    # Return the topic URLs in JSON format
    return jsonify({"movies": topic_urls})

if __name__ == "__main__":
    app.run(debug=True)
