import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL awal untuk scraping
url = 'https://www.tempo.co/indeks'

# Mengirim request ke halaman
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Mengambil elemen berita
articles = soup.find_all('div', class_='title')

# Menyimpan hasil scraping
data = []
for article in articles:
    title = article.a.text.strip()
    link = article.a['href']
    data.append({'title': title, 'link': link})

# Simpan ke CSV
df = pd.DataFrame(data)
df.to_csv('tempo_news.csv', index=False)
