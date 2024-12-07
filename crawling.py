import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin, urlparse

# URL awal untuk crawling
start_url = 'https://www.tempo.co/indeks'
max_depth = 2            # Kedalaman maksimum crawling
max_links_per_depth = 10 # Jumlah maksimum link per kedalaman
visited_links = set()    # Set untuk menyimpan link yang sudah dikunjungi
crawled_links = []       # List untuk menyimpan link yang sesuai regex

# File output
crawl_output_file = 'crawl.txt'
scraping_output_file = 'scrapping.csv'

# Regex pattern untuk mencocokkan link artikel Tempo
article_pattern = re.compile(r'https://www\.tempo\.co/[a-z0-9-]+/[a-z0-9-]+-\d+$')

# Membuka file untuk menyimpan link dan hasil scraping
crawl_file = open(crawl_output_file, 'w')
scraping_file = open(scraping_output_file, 'w')
scraping_file.write('title,link\n')  # Menulis header CSV

def crawl(url, depth):
    """Fungsi untuk melakukan crawling dengan kedalaman tertentu."""
    if depth > max_depth:
        return
    if url in visited_links:
        return

    print(f"📡 Crawling (Depth {depth}): {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Gagal mengakses {url}: {e}")
        return

    visited_links.add(url)  # Tandai URL ini sebagai sudah dikunjungi

    # Parsing halaman
    soup = BeautifulSoup(response.text, 'html.parser')

    # Mengambil semua elemen <a> dengan atribut href
    links_found = 0
    for a in soup.find_all('a', href=True):
        link = urljoin(url, a['href'])
        
        # Hanya mengambil link yang sesuai dengan pola regex
        if article_pattern.match(link):
            if link not in visited_links:
                print(f"🔗 Ditemukan link sesuai pola: {link}")
                links_found += 1
                crawled_links.append(link)
                
                # Simpan link yang dicrawl langsung ke file
                crawl_file.write(link + '\n')
                crawl_file.flush()  # Pastikan data langsung ditulis ke file
                
                # Rekursif crawl ke link yang ditemukan
                if links_found <= max_links_per_depth:
                    crawl(link, depth + 1)

                # Jika sudah mencapai batas maksimal link di kedalaman ini, berhenti
                if links_found >= max_links_per_depth:
                    print(f"🚫 Mencapai batas maksimal {max_links_per_depth} link di kedalaman {depth}")
                    break

def scrape_links():
    """Melakukan scraping judul dari link yang telah dicrawl dan menyimpan hasilnya langsung ke file CSV."""
    with open(crawl_output_file, 'r') as f:
        links = f.read().splitlines()

    for link in links:
        print(f"🔍 Scraping: {link}")
        try:
            response = requests.get(link, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Mengambil judul artikel (jika tersedia)
            title_tag = soup.find('title')
            title = title_tag.text.strip() if title_tag else 'Judul tidak ditemukan'

            # Menyimpan hasil scraping langsung ke file CSV
            scraping_file.write(f'"{title}","{link}"\n')
            scraping_file.flush()  # Pastikan data langsung ditulis ke file

            print(f"✅ Berhasil mengambil judul: {title}")
            time.sleep(0.5)  # Delay untuk menghindari rate-limiting

        except requests.exceptions.RequestException as e:
            print(f"❌ Gagal mengakses {link}: {e}")

# Mulai proses crawling
print(f"🚀 Memulai crawling dari {start_url}")
crawl(start_url, depth=1)

# Tutup file setelah crawling selesai
crawl_file.close()

# Lakukan scraping pada link yang sudah dikumpulkan
scrape_links()

# Tutup file setelah scraping selesai
scraping_file.close()

print(f"\n💾 Hasil crawling disimpan di {crawl_output_file}")
print(f"💾 Hasil scraping disimpan di {scraping_output_file}")
