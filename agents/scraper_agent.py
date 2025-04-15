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
        ARTICLE_URL = f"{BASE_URL}/learn/trading-guide?page=2"
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = uc.Chrome(options=options, version_main=134)
        driver.get(ARTICLE_URL)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.fw-content.fw-content--single-article.line-numbers'))
            )
        except Exception as e:
            print("❌ Failed to load article content.")
            driver.quit()
            raise e

        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        article_div = soup.select_one('div.fw-content.fw-content--single-article.line-numbers')

        # Extract title
        title_tag = soup.find("h1")
        title = title_tag.text.strip() if title_tag else "No title found"

        # Extract content
        content_blocks = []
        for elem in article_div.find_all(['h2', 'h3', 'h4', 'p', 'ul', 'li', 'span', 'img']):
            if elem.name in ['h2', 'h3', 'h4']:
                content_blocks.append(f"<h2>{elem.get_text(strip=True)}</h2>")
            elif elem.name == 'p':
                content_blocks.append(f"<p>{elem.get_text(strip=True)}</p>")
            elif elem.name == 'ul':
                ul_content = "<ul>" + "".join(f"<li>{li.get_text(strip=True)}</li>" for li in elem.find_all('li')) + "</ul>"
                content_blocks.append(ul_content)
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

        print(f"✅ Title: {title}")
        print("✅ Article Content:\n")
        print("".join(content_blocks))

        return [{
            "title": title,
            "url": ARTICLE_URL,
            "content": "".join(content_blocks)
        }]
