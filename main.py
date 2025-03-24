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
    print("Getting article links...")
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)

    driver.get(f"{BASE_URL}/learn/trading-guide")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    links = []
    for a in soup.select('a[href^="/learn/"]'):
        full_link = BASE_URL + a.get('href')
        if full_link not in links and "trading-guide" not in full_link:
            links.append(full_link)
    print(f"Found {len(links)} articles.")
    return links

def scrape_article(url):
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)

    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    try:
        title = soup.find("h1").text.strip()
        content_paragraphs = soup.find_all(['p', 'h2', 'h3'])
        content = "\n".join(p.get_text(strip=True) for p in content_paragraphs)
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and src.startswith('http'):
                images.append(src)
            elif src and src.startswith('/'):
                images.append(BASE_URL + src)
        return {"url": url, "title": title, "content": content, "images": images}
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def translate_text(content):
    if not content or not isinstance(content, str) or not content.strip():
        return "Translation failed"

    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    prompt = (
        f"Translate this text into Malay (Bahasa Malaysia). "
        "Only return the translated text structured like an article. "
        "Please exclude or remove any sentences that look like advertisements from the text. "
        "Here is the text:\n\n"
        f"{content}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    for attempt in range(5):
        try:
            response = requests.post(gemini_url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                translated = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return translated.strip() if translated else "Translation failed"
            elif response.status_code == 429:
                print(f"[Rate Limit] Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)
            else:
                print(f"[Gemini Error] {response.status_code}: {response.text}")
                return "Translation failed"
        except Exception as e:
            print(f"[Gemini Exception] {e}")
            return "Translation failed"
    return "Translation failed"

def save_articles(articles):
    filename = "mexc_translated_articles.json"  # Always overwrite the same file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "articles": articles
        }, f, ensure_ascii=False, indent=4)
    print(f"✅ Saved {len(articles)} articles to {filename}")

def main():
    if not GOOGLE_API_KEY:
        print("[ERROR] GEMINI_API_KEY is not set!")
        return

    articles_data = []
    links = get_article_links()
    for link in links:
        print(f"\n🔎 Scraping: {link}")
        article = scrape_article(link)
        if article:
            max_retries = 3
            for attempt in range(max_retries):
                translated_content = translate_text(article['content'])
                if translated_content != "Translation failed":
                    break
                print(f"[Retry {attempt + 1}] Translation failed for: {article['title']}")
                time.sleep(2)
            else:
                print(f"[SKIP] Failed to translate after {max_retries} attempts: {article['title']}")
                continue

            article['translated_content'] = translated_content
            articles_data.append(article)
            time.sleep(2)
    save_articles(articles_data)

if __name__ == "__main__":
    main()
