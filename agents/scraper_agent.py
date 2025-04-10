from crewai import Agent
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

class ScraperAgent(Agent):
    def run(self):
        BASE_URL = "https://hata.freshdesk.com"
        logging.info("Scraping articles from Hata Learn...")

        # Step 1: Launch browser and load /support/solutions page
        options_main = uc.ChromeOptions()
        options_main.add_argument('--headless=new')
        options_main.add_argument('--no-sandbox')
        options_main.add_argument('--disable-dev-shm-usage')

        driver = uc.Chrome(options=options_main, version_main=134)
        driver.get(f"{BASE_URL}/support/solutions")
        time.sleep(3)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.solution-category'))
            )
        except Exception as e:
            logging.error("❌ Element 'div.solution-category' not found. Saving HTML for debugging.")
            with open("debug_hata_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            driver.quit()
            raise e

        # Scroll to bottom to trigger lazy-loading
        scroll_pause_time = 2
        last_height = driver.execute_script("return document.body.scrollHeight")

        for _ in range(4):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        # Step 2: Collect all valid article links
        links = []
        for a in soup.select('a[href^="/support/solutions/articles/"]'):
            href = a.get('href')
            full_link = BASE_URL + href
            if full_link not in links:
                links.append(full_link)

        logging.debug(f"Links found: {links}")
        logging.info(f"✅ Found {len(links)} articles.")

        # Step 3: Scrape each article
        articles = []
        for idx, link in enumerate(links):
            logging.info(f"🔎 Scraping article {idx+1}/{len(links)}: {link}")

            options = uc.ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            driver = uc.Chrome(options=options, version_main=134)
            driver.get(link)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.article-content'))
                )
            except Exception as e:
                logging.warning(f"⚠️ Article content not found at {link}")
                driver.quit()
                continue

            time.sleep(2)
            page_soup = BeautifulSoup(driver.page_source, "html.parser")
            driver.quit()

            title_tag = page_soup.find("h1")
            title = title_tag.text.strip() if title_tag else "No title found"
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

        logging.info(f"✅ Scraping completed. Total articles scraped: {len(articles)}")
        return articles
