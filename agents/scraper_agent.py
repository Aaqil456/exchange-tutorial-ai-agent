from crewai import Agent
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

class ScraperAgent(Agent):
    def run(self):
        BASE_URL = "https://explore.hata.io"
        print("Scraping articles from Hata Learn...")

        # Step 1: Get article links
        options_main = uc.ChromeOptions()
        options_main.add_argument('--headless')
        options_main.add_argument('--no-sandbox')
        options_main.add_argument('--disable-dev-shm-usage')
        driver = uc.Chrome(options=options_main, version_main=134)

        driver.get(f"{BASE_URL}/learn")
        time.sleep(5)  # ⏳ Let React load articles
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        links = []
        for a in soup.select('a[href^="/learn/"]'):
            href = a.get('href')
            full_link = BASE_URL + href
            if full_link not in links and href.count("/") == 2:  # filter only main articles
                links.append(full_link)

        print(f"✅ Found {len(links)} articles.")

        # Step 2: Scrape each article
        articles = []
        for idx, link in enumerate(links):
            print(f"🔎 Scraping article {idx + 1}/{len(links)}: {link}")

            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = uc.Chrome(options=options, version_main=134)

            driver.get(link)
            time.sleep(5)  # ⏳ Let full content render
            page_soup = BeautifulSoup(driver.page_source, "html.parser")
            driver.quit()

            # Extract title
            title_tag = page_soup.find("h1")
            title = title_tag.get_text(strip=True) if title_tag else "No title found"

            content_blocks = []
            for elem in page_soup.find_all(['h2', 'h3', 'p', 'ul', 'blockquote', 'pre', 'span', 'img']):
                if elem.name in ['h2', 'h3']:
                    content_blocks.append(f"<h2>{elem.get_text(strip=True)}</h2>")
                elif elem.name == 'p':
                    content_blocks.append(f"<p>{elem.get_text(strip=True)}</p>")
                elif elem.name == 'ul':
                    ul_content = "<ul>" + "".join(f"<li>{li.get_text(strip=True)}</li>" for li in elem.find_all('li')) + "</ul>"
                    content_blocks.append(ul_content)
                elif elem.name == 'blockquote':
                    content_blocks.append(f"<blockquote>{elem.get_text(strip=True)}</blockquote>")
                elif elem.name == 'pre':
                    content_blocks.append(f"<pre>{elem.get_text(strip=True)}</pre>")
                elif elem.name == 'span':
                    text = elem.get_text(strip=True)
                    if text:
                        content_blocks.append(f"<p>{text}</p>")
                elif elem.name == 'img':
                    src = elem.get('src')
                    if src:
                        if src.startswith('/'):
                            src = BASE_URL + src
                        content_blocks.append(f'<img src="{src}" alt="tutorial image" />')

            articles.append({
                "url": link,
                "title": title,
                "content": "".join(content_blocks)
            })

        print(f"✅ Scraping completed. Total articles scraped: {len(articles)}")
        return articles
