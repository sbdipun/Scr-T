from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Tamilmv scraping function
def tamilmv():
    mainUrl = 'https://www.1tamilmv.legal/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    movie_list = []
    real_dict = {}

    response = requests.get(mainUrl, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    temps = soup.find_all('div', {'class': 'ipsType_break ipsContained'})

    if len(temps) < 21:
        return [], {}

    for i in range(21):
        title = temps[i].findAll('a')[0].text.strip()
        link = temps[i].find('a')['href']
        movie_list.append(title)

        movie_details = get_movie_details(link)
        real_dict[title] = movie_details

    return movie_list, real_dict

# Function to get movie details
def get_movie_details(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        mag = [a['href'] for a in soup.find_all('a', href=True) if 'magnet:' in a['href']]
        filelink = [a['href'] for a in soup.find_all('a', {"data-fileext": "torrent", 'href': True})]

        movie_details = []
        movie_title = soup.find('h1').text.strip()

        for p in range(len(mag)):
            if p < len(filelink):
                movie_details.append(f"<b>📂 Movie Title:</b> {movie_title}\n🧲 <code>{mag[p]}</code>\n\n🗒️-> <a href='{filelink[p]}'>Torrent File Download 🖇</a>")
            else:
                movie_details.append(f"<b>📂 Movie Title:</b> {movie_title}\n🧲 <code>{mag[p]}</code>\n\n🗒️-> <a href='#'>Torrent File Download 🖇</a>")

        return movie_details
    except Exception as e:
        print(f"Error retrieving movie details: {e}")
        return []

@app.route('/scrape', methods=['GET'])
def scrape():
    movie_list, real_dict = tamilmv()
    return jsonify({'movies': movie_list, 'details': real_dict})

if __name__ == '__main__':
    app.run(debug=True)
