from crewai import Agent
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import logging

# Set up logging to print detailed debug information
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

class ScraperAgent(Agent):
    def run(self):
        BASE_URL = "https://hata.freshdesk.com/"
        logging.info("Scraping articles from Hata Learn...")

        # Step 1: Launch browser and load /learn page
        options_main = uc.ChromeOptions()
        options_main.add_argument('--headless')
        options_main.add_argument('--no-sandbox')
        options_main.add_argument('--disable-dev-shm-usage')

        driver = uc.Chrome(options=options_main, version_main=134)  # ✅ Version locked

        driver.get(f"{BASE_URL}/support/solutions")
        time.sleep(3)  # ⏳ Initial delay

        # Scroll to bottom to trigger lazy-loading
        scroll_pause_time = 2
        last_height = driver.execute_script("return document.body.scrollHeight")
        logging.debug(f"DEBUG: Initial page height: {last_height}")

        for _ in range(4):  # You can increase this if needed
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            logging.debug(f"DEBUG: New page height after scroll: {new_height}")
            if new_height == last_height:
                logging.info("DEBUG: No new content loaded after scroll.")
                break
            last_height = new_height

        # Step 2: Parse final loaded HTML
        page_source = driver.page_source
        logging.debug(f"DEBUG: Page source snippet: {page_source[:2000]}")  # Print the first 2000 characters
        soup = BeautifulSoup(page_source, "html.parser")
        driver.quit()

        # Step 3: Collect all valid article links
        links = []
        links_elements = soup.select('a[href^="/learn/"]')
        logging.debug(f"DEBUG: Found {len(links_elements)} links matching 'a[href^=\"/learn/\"]'.")

        for elem in links_elements:
            href = elem.get('href')
            full_link = BASE_URL + href
            if full_link not in links and "/learn/" in href and href.count("/") == 2:  # Avoid nested routes or duplicates
                links.append(full_link)

        logging.info(f"✅ Found {len(links)} articles.")

        # Step 4: Scrape each article
        articles = []
        for idx, link in enumerate(links):
            logging.info(f"🔎 Scraping article {idx+1}/{len(links)}: {link}")

            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            driver = uc.Chrome(options=options, version_main=134)
            driver.get(link)
            time.sleep(2)  # Optional delay to ensure full render
            page_soup = BeautifulSoup(driver.page_source, "html.parser")
            driver.quit()

            title_tag = page_soup.find("h1")
            title = title_tag.text.strip() if title_tag else "No title found"
            logging.debug(f"DEBUG: Article title: {title}")
            
            content_blocks = []

            # Extract structured tutorial content
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
