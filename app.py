from flask import Flask, jsonify, Response
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)



# For Vercel compatibility
@app.route('/')
def home():
    return "Welcome to the TamilMV Scraper API. Use /scrape to get JSON data or /rss for an RSS feed."

if __name__ == '__main__':
    app.run(debug=True)
