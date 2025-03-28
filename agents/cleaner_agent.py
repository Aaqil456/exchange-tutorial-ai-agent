import requests
import os
import time
from agents.base_agent import BaseAgent

# Load Gemini API key
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")

class CleanerAgent(BaseAgent):
    def run(self, articles):
        print("🧹 Cleaning articles with LLM assistance...")
        cleaned_articles = []

        for article in articles:
            decision = self.llm_decide(article)

            if decision.lower() == "keep":
                cleaned_content = self.clean_content(article["content"])
                article["content"] = cleaned_content
                print(f"✅ Keeping: {article['title']}")
                cleaned_articles.append(article)
            else:
                print(f"🚫 Skipping: {article['title']}")

            time.sleep(1)  # Respect Gemini API rate limits

        print(f"✅ Cleaning complete. Articles kept: {len(cleaned_articles)}")
        return cleaned_articles

    def llm_decide(self, article):
        prompt = (
            "You are an expert tutorial content reviewer. "
            "Analyze the following article and decide if it is a structured tutorial containing clear steps, headings, explanations, and helpful images. "
            "If yes, reply with 'Keep'. If it is promotional, too short, repetitive, or unstructured, reply with 'Skip'. "
            "Only reply with either 'Keep' or 'Skip' without additional sentences.\n\n"
            f"Title: {article.get('title', '')}\n"
            f"Content:\n{article.get('content', '')}\n\n"
            "Your decision:"
        )

        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]}
            )

            if response.status_code == 200:
                decision_text = (
                    response.json()
                    .get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                print(f"🤖 LLM Decision: {decision_text.strip()}")
                return decision_text.strip()
            else:
                print(f"⚠️ LLM API error {response.status_code}: {response.text}")
                return "Skip"

        except Exception as e:
            print(f"❌ Exception during LLM call: {e}")
            return "Skip"

    def clean_content(self, html_content):
        prompt = (
            "You are a content cleaner. Remove any non-informative parts like promotional text, footers, and irrelevant images from this HTML content. "
            "Keep important text, headings, and tutorial images. Only return clean HTML:\n\n"
            f"{html_content}"
        )

        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]}
            )

            if response.status_code == 200:
                cleaned_html = (
                    response.json()
                    .get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                return cleaned_html
            else:
                print(f"⚠️ Gemini API content clean error {response.status_code}: {response.text}")
                return html_content

        except Exception as e:
            print(f"❌ Error cleaning content: {e}")
            return html_content
