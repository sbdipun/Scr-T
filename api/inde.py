# from flask import Flask, jsonify, Response
# import requests
# import random
# from bs4 import BeautifulSoup
# import re
# import urllib.parse
# import html
# from urllib.parse import quote_plus, urlparse, quote, parse_qs

# # Initialize Flask app
# app = Flask(__name__)

# # Base URL to scrape
# base_url = "https://www.1tamilblasters.wine"

# # Function to scrape the latest links and magnet links
# def scrape_links():
#     try:
#         # Enhanced headers
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#             'Accept-Language': 'en-US,en;q=0.5',
#             'Referer': 'https://www.google.com/',
#             'Connection': 'keep-alive',
#             'Upgrade-Insecure-Requests': '1'
#         }

#         # Proxy rotation (optional)
#         proxies = [
#             {'https': 'https://ogais4d6kcfVkEyuGy3nz1mT:GuRA1qAXgoi85mW9GZYJsJKN@in160.nordvpn.com:89'}
#         ]
#         proxy = random.choice(proxies)

#         # Make the request
#         response = requests.get(base_url, proxies=proxy, headers=headers, timeout=10)
#         response.raise_for_status()

#         # Parse the HTML
#         soup = BeautifulSoup(response.text, 'html.parser')
#         divs = soup.find_all('div', class_='ipsType_break ipsContained')

#         # Limit to 10 links to prevent timeout
#         links = [div.find('a')['href'] for div in divs[:10] if div.find('a')]

#         results = []
#         for link in links:
#             sub_response = requests.get(link, headers=headers, timeout=10)
#             sub_response.raise_for_status()

#             sub_soup = BeautifulSoup(sub_response.text, 'html.parser')
#             magnet_link_tag = sub_soup.find('a', class_='magnet-plugin')

#             if magnet_link_tag and 'href' in magnet_link_tag.attrs:
#                 magnet_link = magnet_link_tag['href']
#                 query_params = re.search(r'dn=([^&]+)', magnet_link)
#                 title = query_params.group(1) if query_params else 'No Title'
#                 decoded_title = urllib.parse.unquote(title)

#                 description = f"."
#                 safe_description = html.escape(description)

#                 results.append({
#                     "title": decoded_title,
#                     "magnet_link": magnet_link,
#                     "description": safe_description
#                 })
#         return results
#     except requests.exceptions.RequestException as e:
#         print(f"Request failed: {e}")
#         return []

# # Home Route - Returns JSON
# @app.route("/")
# def home():   
#     return jsonify({"message": "Welcome to TamilBlasters RSS FEED Site. Use /rss end of the Url and BooM!! Developed By Mr. Shaw"})

# # RSS Route - Returns XML
# @app.route('/rss')
# def rss():
#     data = scrape_links()

#     # Build the RSS XML feed
#     rss_items = ""
#     for item in data:
#         rss_items += f"""
#             <item>
#                 <title>{html.escape(item['title'])}</title>
#                 <link>{html.escape(item['magnet_link'])}</link>
#                 <description>{item['description']}</description>
#             </item>
#         """

#     rss_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
#         <rss version="2.0">
#             <channel>
#                 <title>Tamil Blasters RSS Feed</title>
#                 <link>{base_url}</link>
#                 <description>Latest Movies and TV Shows</description>
#                 {rss_items}
#             </channel>
#         </rss>
#     """

#     return Response(rss_feed, mimetype='application/rss+xml')

# # Run the Flask app
# if __name__ == '__main__':
#     app.run(debug=True)
