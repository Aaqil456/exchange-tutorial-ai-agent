import requests
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import os
import json
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    for a in soup.select('a[href^="/learn/article/"]'):
        full_link = BASE_URL + a.get('href')
        if full_link not in links:
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

    # Wait until h1 or content is present
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
    except Exception:
        print(f"Timeout waiting for content at {url}")
        driver.quit()
        return None

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    try:
        title = soup.find("h1").text.strip()
        meta_description = soup.find("meta", {"name": "description"})
        meta_desc_text = meta_description["content"] if meta_description else ""

        published_date = ""
        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            published_date = time_tag.get("datetime")

        content_blocks = []
        images = []

        # Try scraping structured content from headings, paragraphs, and images
        elements = soup.find_all(['h2', 'h3', 'p', 'img'])
        if elements:
            for element in elements:
                if element.name in ['h2', 'h3']:
                    text = element.get_text(strip=True)
                    if text:
                        content_blocks.append({"type": "heading", "text": text})
                elif element.name == 'p':
                    text = element.get_text(strip=True)
                    if text:
                        content_blocks.append({"type": "paragraph", "text": text})
                elif element.name == 'img':
                    src = element.get('src')
                    if src:
                        if src.startswith('/'):
                            src = BASE_URL + src
                        images.append(src)
                        content_blocks.append({"type": "image", "url": src})
        else:
            # Fallback to parsing application/ld+json if content is dynamic
            script_tag = soup.find("script", type="application/ld+json")
            if script_tag:
                try:
                    data_json = json.loads(script_tag.string)
                    article_body = data_json.get("articleBody", "")
                    if article_body:
                        for para in article_body.split('\n'):
                            if para.strip():
                                content_blocks.append({"type": "paragraph", "text": para.strip()})
                        images.append(data_json.get("image")) if data_json.get("image") else None
                        print(f"Used JSON-LD fallback for {url}")
                except Exception as e:
                    print(f"Error parsing JSON-LD at {url}: {e}")

        if not content_blocks:
            print(f"No content found for {url}. Skipping.")
            return None

        return {
            "url": url,
            "title": title,
            "meta_description": meta_desc_text,
            "published_date": published_date,
            "content_blocks": content_blocks,
            "images": images
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def translate_text_block(block_text):
    if not block_text.strip():
        return ""

    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    prompt = (
        f"Translate this text into Malay (Bahasa Malaysia). "
        "Only return the translated text structured like an article. "
        "Exclude any promotional or advertisement lines. "
        "Here is the text:\n\n"
        f"{block_text}"
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
                return translated.strip() if translated else ""
            elif response.status_code == 429:
                print(f"[Rate Limit] Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)
            else:
                print(f"[Gemini Error] {response.status_code}: {response.text}")
                return ""
        except Exception as e:
            print(f"[Gemini Exception] {e}")
            return ""
    return ""

def translate_article_blocks(content_blocks):
    translated_blocks = []
    for block in content_blocks:
        if block["type"] in ["heading", "paragraph"]:
            translated_text = translate_text_block(block["text"])
            translated_blocks.append({
                "type": block["type"],
                "original_text": block["text"],
                "translated_text": translated_text
            })
        elif block["type"] == "image":
            translated_blocks.append(block)
        time.sleep(1)
    return translated_blocks

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
            print(f"🌐 Translating blocks for: {article['title']}")
            translated_blocks = translate_article_blocks(article["content_blocks"])
            article["translated_blocks"] = translated_blocks
            articles_data.append(article)
    save_articles(articles_data)

if __name__ == "__main__":
    main()
