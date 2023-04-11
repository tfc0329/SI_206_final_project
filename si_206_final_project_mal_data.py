from bs4 import BeautifulSoup
import sqlite3
import requests

url = 'https://api.myanimelist.net/v2/anime?q=one&limit=4'
resp = requests.get(url)
print(resp)