from crewai import Agent
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ScraperAgent(Agent):
    def run(self, *args, **kwargs):
        BASE_URL = "https://www.mexc.co"
        ARTICLE_LIST_URL = f"{BASE_URL}/learn/trading-guide?page=2"
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = uc.Chrome(options=options, version_main=134)
        driver.get(ARTICLE_LIST_URL)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.m-card.learn-list-card'))
            )
        except Exception as e:
            print("❌ Failed to load MEXC list page.")
            driver.quit()
            raise e

        soup = BeautifulSoup(driver.page_source, "html.parser")
        article_cards = soup.select('.m-card.learn-list-card')
        article_links = [BASE_URL + card.find('a')['href'] for card in article_cards if card.find('a')]

        articles = []

        for link in article_links[:1]:  # 👈 Scrape 1 dulu (boleh ubah ke banyak)
            try:
                driver.get(link)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.article-detail-container'))
                )
                time.sleep(1)
                article_soup = BeautifulSoup(driver.page_source, "html.parser")

                title_tag = article_soup.find("h1")
                title = title_tag.text.strip() if title_tag else "No title found"

                content_div = article_soup.select_one('.article-detail-container')
                content_blocks = []

                for elem in content_div.find_all(['h2', 'h3', 'p', 'ul', 'li', 'img']):
                    if elem.name in ['h2', 'h3']:
                        content_blocks.append(f"<h2>{elem.get_text(strip=True)}</h2>")
                    elif elem.name == 'p':
                        content_blocks.append(f"<p>{elem.get_text(strip=True)}</p>")
                    elif elem.name == 'ul':
                        content_blocks.append("<ul>" + "".join(f"<li>{li.get_text(strip=True)}</li>" for li in elem.find_all('li')) + "</ul>")
                    elif elem.name == 'img':
                        src = elem.get('src')
                        if src:
                            if src.startswith('/'):
                                src = BASE_URL + src
                            content_blocks.append(f'<img src="{src}" alt="tutorial image" />')

                print(f"✅ Title: {title}")
                print("✅ Article Content:\n")
                print("".join(content_blocks))

                articles.append({
                    "title": title,
                    "url": link,
                    "content": "".join(content_blocks)
                })

            except Exception as e:
                print(f"❌ Failed to load article from {link}")
                continue

        driver.quit()
        return articles
