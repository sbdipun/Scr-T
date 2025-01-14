from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse

# Initialize Flask app
app = Flask(__name__)

# Base URL to scrape
base_url = "https://www.1tamilblasters.party/"

# Headers for requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

# Function to scrape the latest 25-30 links and magnet links
def scrape_links():
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()

        if 'text/html' in response.headers['Content-Type']:
            soup = BeautifulSoup(response.text, 'html.parser')
            divs = soup.find_all('div', class_='ipsType_break ipsContained')

            # Limit to 25-30 links
            links = []
            for div in divs[:30]:
                link_tag = div.find('a')
                if link_tag and 'href' in link_tag.attrs:
                    links.append(link_tag['href'])

            results = []
            for link in links:
                sub_response = requests.get(link, headers=headers, timeout=10)
                sub_response.raise_for_status()

                sub_soup = BeautifulSoup(sub_response.text, 'html.parser')
                magnet_link_tag = sub_soup.find('a', class_='magnet-plugin')

                if magnet_link_tag and 'href' in magnet_link_tag.attrs:
                    magnet_link = magnet_link_tag['href']
                    query_params = parse_qs(urlparse(magnet_link).query)
                    title = query_params.get('dn', ['No Title'])[0]
                    results.append({"title": title, "magnet_link": magnet_link})
            return results
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []

# Route 1: Home - Returns JSON data
@app.route("/")
def home():   
    return jsonify({"message": "Welcome to TamilMV RSS FEED Site. Use /rss end of the Url and BooM!! Developed By Mr. Shaw"})
    

# Route 2: RSS (JSON format)
@app.route('/rss')
def rss():
    data = scrape_links()
    return jsonify(data)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
