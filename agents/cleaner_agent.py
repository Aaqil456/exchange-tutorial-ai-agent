import requests
import os
import time
import re
from bs4 import BeautifulSoup
from agents.base_agent import BaseAgent  # ✅ Absolute import

# Read Gemini API Key from environment
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")

class CleanerAgent(BaseAgent):
    def run(self, articles):
        print("🧹 Cleaning articles with LLM assistance (text + image filtering)...")
        cleaned_articles = []

        for article in articles:
            decision = self.llm_decide_article(article)

            if decision.lower() == "keep":
                print(f"✅ Keeping: {article['title']}")

                # Clean irrelevant images
                filtered_content = self.filter_irrelevant_images(article['content'])
                article['content'] = filtered_content

                cleaned_articles.append(article)
            else:
                print(f"🚫 Skipping: {article['title']}")

            time.sleep(1)  # Respect Gemini API rate limits

        print(f"✅ Cleaning complete. Articles kept: {len(cleaned_articles)}")
        return cleaned_articles

    def llm_decide_article(self, article):
        prompt = (
            "You are an expert tutorial content reviewer. "
            "Analyze the following article and decide if it is a structured tutorial containing clear steps, headings, explanations, and helpful images. "
            "If yes, reply with 'Keep'. If it is promotional, too short, repetitive, or unstructured, reply with 'Skip'. "
            "Only reply with either 'Keep' or 'Skip' without additional sentences.\n\n"
            f"Title: {article.get('title', '')}\n"
            f"Content:\n{article.get('content', '')}\n\n"
            "Your decision:"
        )
        return self.ask_gemini(prompt)

    def filter_irrelevant_images(self, html):
        soup = BeautifulSoup(html, "html.parser")
        images = soup.find_all("img")

        for img in images:
            context = self.extract_image_context(soup, img)
            prompt = (
                "You are a tutorial optimization assistant. Analyze the following image and its context. "
                "If the image is useful to the tutorial (e.g. shows a screenshot, a chart, or explains a step), respond with 'Keep'. "
                "If it is decorative, branding, unrelated, or a footer image (e.g. MEXC logo, bonus banner, social icons), respond with 'Remove'. "
                "Only reply 'Keep' or 'Remove'.\n\n"
                f"Image src: {img.get('src')}\n"
                f"Surrounding Context:\n{context}\n\n"
                "Your decision:"
            )

            decision = self.ask_gemini(prompt)
            if decision.lower() == "remove":
                print(f"🗑️ Removing image: {img.get('src')}")
                img.decompose()
            else:
                print(f"🖼️ Keeping image: {img.get('src')}")

            time.sleep(1)

        return str(soup)

    def extract_image_context(self, soup, img_tag):
        # Get nearby text around the image
        context = []
        for tag in img_tag.find_all_previous(limit=3):
            if tag.name in ["p", "h1", "h2", "h3"]:
                context.append(tag.get_text(strip=True))
        for tag in img_tag.find_all_next(limit=3):
            if tag.name in ["p", "h1", "h2", "h3"]:
                context.append(tag.get_text(strip=True))
        return "\n".join(context).strip()

    def ask_gemini(self, prompt):
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]}
            )

            if response.status_code == 200:
                return (
                    response.json()
                    .get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                    .strip()
                )
            else:
                print(f"⚠️ Gemini API error {response.status_code}: {response.text}")
                return "Keep"  # default to keep if uncertain
        except Exception as e:
            print(f"❌ Gemini call error: {e}")
            return "Keep"
