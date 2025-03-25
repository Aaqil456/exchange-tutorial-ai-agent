from crewai import Agent
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

class ScraperAgent(Agent):
    def run(self):
        BASE_URL = "https://www.mexc.co"
        print("Scraping articles...")
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        driver = uc.Chrome(options=options)
        driver.get(f"{BASE_URL}/learn/trading-guide")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        links = []
        for a in soup.select('a[href^="/learn/"]'):
            full_link = BASE_URL + a.get('href')
            if full_link not in links and "trading-guide" not in full_link:
                links.append(full_link)

        articles = []
        for link in links:
            driver = uc.Chrome(options=options)
            driver.get(link)
            page_soup = BeautifulSoup(driver.page_source, "html.parser")
            driver.quit()

            title = page_soup.find("h1").text.strip()
            content_blocks = []

            # Gather content in sequence, including <span> and <img>
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
                    content_blocks.append(f"<p>{elem.get_text(strip=True)}</p>")
                elif elem.name == 'img':
                    src = elem.get('src')
                    if src.startswith('/'):
                        src = BASE_URL + src
                    content_blocks.append(f'<img src="{src}" alt="tutorial image" />')

            articles.append({
                "url": link,
                "title": title,
                "content": "".join(content_blocks)
            })

        return articles
