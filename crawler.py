import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import time
import random

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def request_with_retries(url, retries=3, delay=1):
    for attempt in range(retries):
        try:
            headers = {'User-Agent': get_random_user_agent()}
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Untuk mengangkat HTTPError jika terjadi error
            return response
        except (requests.RequestException, requests.HTTPError) as e:
            print(f"Request failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Penundaan eksponensial
    raise Exception("Max retries exceeded")


def extract_article_links(index_url):
    links = []
    while True:
        response = request_with_retries(index_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        articles = soup.find_all('h2', class_='title')
        for article in articles:
            a_tag = article.find('a')
            link = a_tag.get('href')
            if link and link.startswith('/'):
                link = f'https://www.tempo.co{link}'
            if link not in links:
                links.append(link)

        next_page = soup.find('a', class_='next')
        if next_page and 'href' in next_page.attrs:
            index_url = f'https://www.tempo.co{next_page["href"]}'
        else:
            break

        time.sleep(random.uniform(3, 7))  # Randomized delay

    return links

def extract_article_data(url):
    response = request_with_retries(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Ekstrak judul
    title_tag = soup.find('h1', class_='title margin-bottom-sm')
    title = title_tag.get_text(strip=True) if title_tag else ''

    # Ekstrak reporter dan editor
    block_avatar = soup.find('div', class_='block-avatar')
    reporter, editor = '', ''
    if block_avatar:
        title_tags = block_avatar.find_all('p', class_='title bold')
        if len(title_tags) > 0:
            reporter = title_tags[0].get_text(strip=True)
        if len(title_tags) > 1:
            editor = title_tags[1].get_text(strip=True)

    # Ekstrak tanggal dan waktu
    date_time_str = soup.find('p', class_='date margin-bottom-sm')
    date_time = ''
    if date_time_str:
        date_time_str = date_time_str.get_text(strip=True)
        try:
            date_time = datetime.strptime(date_time_str, '%A, %d %B %Y %H:%M WIB')
        except ValueError:
            date_time = date_time_str

    # Ekstrak konten
    content_div = soup.find('div', class_='detail-konten')
    content = []
    if content_div:
        paragraphs = content_div.find_all('p')
        for p in paragraphs:
            if p.find_parent(class_='bacajuga') or p.find_parent(class_='iklan') or 'Pilihan Editor' in p.text:
                continue
            content.append(p.get_text(strip=True))

    content = ' '.join(content)

    return {
        'title': title,
        'reporter': reporter,
        'editor': editor,
        'date_time': date_time,
        'content': content
    }


def load_existing_articles(file_path):
    try:
        df_existing = pd.read_csv(file_path)
        if df_existing.empty:
            print("Existing CSV is empty. Starting fresh.")
            return pd.DataFrame(columns=['title', 'reporter', 'editor', 'date_time', 'content'])
        return df_existing
    except FileNotFoundError:
        print("CSV file not found. Creating a new one.")
        return pd.DataFrame(columns=['title', 'reporter', 'editor', 'date_time', 'content'])
    except pd.errors.EmptyDataError:
        print("CSV file is empty. Creating a new DataFrame.")
        return pd.DataFrame(columns=['title', 'reporter', 'editor', 'date_time', 'content'])
    
def crawl_articles(start_date, end_date, max_articles=50):
    date_format = '%Y-%m-%d'

    # Load existing data from the CSV file
    existing_df = load_existing_articles('articles_data.csv')
    existing_articles = set(zip(existing_df['title'], existing_df['date_time']))

    # Counter for newly crawled articles
    new_articles_count = 0

    current_date = datetime.strptime(start_date, date_format)

    while new_articles_count < max_articles and current_date >= datetime.strptime(end_date, date_format):
        index_url = f'https://www.tempo.co/indeks/{current_date.strftime(date_format)}/tekno'
        print(f"Crawling articles from {index_url}")

        article_links = extract_article_links(index_url)

        if not article_links:
            print("No more articles found.")
            break

        for link in article_links:
            if new_articles_count >= max_articles:
                break
            try:
                # Extract data from the article
                data = extract_article_data(link)
                article_id = (data['title'], data['date_time'])

                # Only save if the article is new
                if article_id not in existing_articles:
                    df_new = pd.DataFrame([data])
                    df_new.to_csv('articles_data.csv', mode='a', header=not existing_articles, index=False)
                    existing_articles.add(article_id)
                    new_articles_count += 1
                    print(f"Saved article: {data['title']}")
                else:
                    print(f"Duplicate article found: {data['title']}")
            except Exception as e:
                print(f"Error processing {link}: {e}")
            time.sleep(random.uniform(3, 7))  # Randomized delay

        # Move to the previous date
        current_date -= timedelta(days=1)


# sesuaikan dengan keperluan
start_date = '2024-05-17'
end_date = '2024-01-17'
max_articles = 10

crawl_articles(start_date, end_date, max_articles)
print(f"Data telah disimpan ke 'articles_data.csv'")