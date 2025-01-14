from flask import Flask, jsonify, render_template_string, Response
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

# Function to scrape latest links and magnet links
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

# Home Route
@app.route('/')
def home():
    scraped_data = scrape_links()
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Scraped Links</title>
    </head>
    <body>
        <h1>Latest Titles and Magnet Links</h1>
        <ul>
            {% for item in scraped_data %}
            <li>
                <strong>{{ item.title }}</strong><br>
                <a href="{{ item.magnet_link }}">Magnet Link</a>
            </li>
            {% endfor %}
        </ul>
    </body>
    </html>
    '''
    return render_template_string(html_template, scraped_data=scraped_data)

# RSS Route
@app.route('/rss')
def rss():
    scraped_data = scrape_links()
    rss_feed = '''<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
        <channel>
            <title>Latest Titles and Magnet Links</title>
            <link>{base_url}</link>
            <description>RSS feed of the latest titles and magnet links</description>
    '''
    for item in scraped_data:
        rss_feed += f'''
            <item>
                <title>{item["title"]}</title>
                <link>{item["magnet_link"]}</link>
                <description>{item["title"]}</description>
            </item>
        '''
    rss_feed += '''
        </channel>
    </rss>
    '''
    return Response(rss_feed, content_type='application/rss+xml')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
