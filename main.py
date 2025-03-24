import requests
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import os
import json
import time
from datetime import datetime

GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")
BASE_URL = "https://www.mexc.co"

def get_article_links():
    driver = uc.Chrome()
    driver.get(f"{BASE_URL}/learn/trading-guide")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    links = []
    for a in soup.select('a[href^="/learn/"]'):
        full_link = BASE_URL + a.get('href')
        if full_link not in links:
            links.append(full_link)
    print(f"Found {len(links)} articles.")
    return links

def scrape_article(url):
    driver = uc.Chrome()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    try:
        title = soup.find("h1").text.strip()
        content_paragraphs = soup.find_all(['p', 'h2', 'h3'])
        content = "\n".join(p.get_text(strip=True) for p in content_paragraphs)
        images = [img['src'] for img in soup.find_all('img') if img.get('src')]
        return {"url": url, "title": title, "content": content, "images": images}
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def translate_text(content):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"
    prompt = (
        "Translate the following text into Malay (Bahasa Malaysia). "
        "Keep crypto and trading terms in English. Do not add explanations, just pure translation:\n\n"
        f"{content}"
    )
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        translated_text = result['candidates'][0]['content']['parts'][0]['text']
        return translated_text.strip()
    else:
        print("Translation failed:", response.text)
        return "Translation failed."

def save_articles(articles):
    filename = f"mexc_articles_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"Saved {len(articles)} articles to {filename}")

def main():
    articles_data = []
    links = get_article_links()
    for link in links:
        print(f"Scraping: {link}")
        article = scrape_article(link)
        if article:
            print("Translating article...")
            translated_content = translate_text(article['content'])
            article['translated_content'] = translated_content
            articles_data.append(article)
            time.sleep(2)
    save_articles(articles_data)

if __name__ == "__main__":
    main()
