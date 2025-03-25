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
    print(f"Scraping article: {url}")
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

        # ✅ Breadcrumb scraping
        breadcrumb_items = soup.select(".breadcrumb a")
        breadcrumbs = " / ".join([crumb.get_text(strip=True) for crumb in breadcrumb_items])

        # ✅ Build structured content with [IMAGE: url] placeholders
        content_elements = soup.find_all(['h2', 'h3', 'p', 'ul', 'blockquote', 'pre', 'span', 'img'])
        content_blocks = []
        for elem in content_elements:
            if elem.name in ['h2', 'h3']:
                content_blocks.append(f"\n\n## {elem.get_text(strip=True)}\n")
            elif elem.name == 'p':
                content_blocks.append(elem.get_text(strip=True) + "\n\n")
            elif elem.name == 'ul':
                for li in elem.find_all('li'):
                    content_blocks.append(f"• {li.get_text(strip=True)}\n")
                content_blocks.append("\n")
            elif elem.name == 'blockquote':
                content_blocks.append(f"\n> {elem.get_text(strip=True)}\n\n")
            elif elem.name == 'pre':
                content_blocks.append(f"\n[Code Block]\n{elem.get_text(strip=True)}\n\n")
            elif elem.name == 'span':
                span_text = elem.get_text(strip=True)
                if span_text and span_text not in "".join(content_blocks):
                    content_blocks.append(span_text + "\n\n")
            elif elem.name == 'img':
                src = elem.get('src')
                if src:
                    if src.startswith('/'):
                        src = BASE_URL + src
                    content_blocks.append(f"\n[IMAGE: {src}]\n")

        content_combined = "".join(content_blocks).strip()

        # ✅ Related articles scraping
        related_articles = []
        related_section = soup.find("div", class_="related-articles") or soup.find("aside")
        if related_section:
            for rel in related_section.select("a"):
                rel_title = rel.get_text(strip=True)
                rel_url = rel['href'] if rel['href'].startswith("http") else BASE_URL + rel['href']
                if rel_title and rel_url:
                    related_articles.append({"title": rel_title, "url": rel_url})

        return {
            "url": url,
            "title": title,
            "breadcrumbs": breadcrumbs,
            "content": content_combined,
            "related_articles": related_articles
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def translate_content_with_images(content):
    if not content.strip():
        return "Translation failed"

    prompt = (
        "You will be given article content from a crypto trading tutorial in English, "
        "including headings, paragraphs, bullet points, and image placeholders in this format: [IMAGE: image_url]. "
        "Translate the entire content into Malay (Bahasa Malaysia), and reformat it into a clean, structured tutorial style. "
        "Wherever you see [IMAGE: image_url], replace it with a Markdown image tag like this: ![Gambar](image_url) "
        "in that exact position without changing the order. "
        "Maintain all headings, bullet points, quotes, and code blocks. "
        "Do not add advertisements or extra explanations. "
        "Only return the translated tutorial with images embedded in the correct places.\n\n"
        f"{content}"
    )

    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    for attempt in range(5):
        try:
            response = requests.post(gemini_url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                translated_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return translated_text.strip() if translated_text else "Translation failed"
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
    filename = "mexc_translated_articles.json"
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
                translated_content = translate_content_with_images(article['content'])
                if translated_content != "Translation failed":
                    break
                print(f"[Retry {attempt + 1}] Translation failed for: {article['title']}")
                time.sleep(2)
            else:
                print(f"[SKIP] Failed to translate after {max_retries} attempts: {article['title']}")
                continue

            article['translated_tutorial'] = translated_content
            articles_data.append(article)
            time.sleep(2)
    save_articles(articles_data)

if __name__ == "__main__":
    main()
