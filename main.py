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
    print(f"Scraping full HTML from #__next: {url}")
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)

    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    try:
        title = soup.find("h1").text.strip() if soup.find("h1") else "No Title Found"

        # Breadcrumbs (if available)
        breadcrumb_items = soup.select(".breadcrumb a")
        breadcrumbs = " / ".join([crumb.get_text(strip=True) for crumb in breadcrumb_items])

        # ✅ Extract full HTML from the div with id="__next"
        content_div = soup.find("div", id="__next")
        if content_div:
            raw_html = str(content_div)
            raw_html = raw_html.replace('src="/', f'src="{BASE_URL}/')  # fix relative URLs
        else:
            raw_html = ""

        # ✅ Related articles if available
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
            "content_html": raw_html.strip(),
            "related_articles": related_articles
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def save_articles(articles):
    filename = "mexc_full_html_articles.json"  # Save output here
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "articles": articles
        }, f, ensure_ascii=False, indent=4)
    print(f"✅ Saved {len(articles)} articles to {filename}")

def main():
    articles_data = []
    links = get_article_links()
    for link in links:
        article = scrape_article(link)
        if article:
            articles_data.append(article)
            time.sleep(2)
    save_articles(articles_data)

if __name__ == "__main__":
    main()
