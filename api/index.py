from flask import Flask, jsonify
import httpx
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
import asyncio

# Initialize Flask app
app = Flask(__name__)

# Base URL to scrape
base_url = "https://www.1tamilblasters.party/"

# Headers for requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

# Function to scrape links asynchronously
async def scrape_links():
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(base_url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            divs = soup.find_all('div', class_='ipsType_break ipsContained')

            # Limit to 10 links to prevent timeout
            links = [div.find('a')['href'] for div in divs[:10] if div.find('a')]

            results = []
            tasks = [fetch_magnet_link(client, link) for link in links]
            results = await asyncio.gather(*tasks)

            return [result for result in results if result]
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
            return []

# Function to fetch magnet link from each subpage
async def fetch_magnet_link(client, link):
    try:
        response = await client.get(link, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        magnet_link_tag = soup.find('a', class_='magnet-plugin')

        if magnet_link_tag and 'href' in magnet_link_tag.attrs:
            magnet_link = magnet_link_tag['href']
            query_params = parse_qs(urlparse(magnet_link).query)
            title = query_params.get('dn', ['No Title'])[0]
            return {"title": title, "magnet_link": magnet_link}
        return None
    except httpx.RequestError as e:
        print(f"Subpage request failed: {e}")
        return None

# Home Route
@app.route("/")
def home():   
    return jsonify({"message": "Welcome to TamilMV RSS FEED Site. Use /rss end of the Url and BooM!! Developed By Mr. Shaw"})

# RSS Route
@app.route('/rss')
async def rss():
    data = await scrape_links()
    return jsonify(data)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
