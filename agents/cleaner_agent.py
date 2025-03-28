import requests
import os
import time
from agents.base_agent import BaseAgent

# Read Gemini API Key from environment
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")

class CleanerAgent(BaseAgent):
    def run(self, articles):
        print("🧹 Cleaning articles with LLM assistance...")
        cleaned_articles = []

        for article in articles:
            decision = self.llm_decide(article)

            if decision.lower() == "keep":
                cleaned_content = self.clean_content(article)
                article["content"] = cleaned_content
                print(f"✅ Keeping and cleaning: {article['title']}")
                cleaned_articles.append(article)
            else:
                print(f"🚫 Skipping: {article['title']}")

            time.sleep(1)  # Respect API limits

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
            print(f"❌ Exception during LLM decision: {e}")
            return "Skip"

    def clean_content(self, article):
        prompt = (
            "You are an expert content editor. "
            "Remove all footer content, promotional blocks, community links, repeated phrases like 'Daftar untuk bonus', irrelevant text, and anything that is not part of the actual tutorial. "
            "Keep only the structured tutorial with its useful headings, steps, and images.\n\n"
            f"Title: {article.get('title', '')}\n"
            f"Content:\n{article.get('content', '')}\n\n"
            "Cleaned content:"
        )

        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]}
            )

            if response.status_code == 200:
                cleaned = (
                    response.json()
                    .get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                return cleaned.strip()
            else:
                print(f"⚠️ Gemini cleaning API error {response.status_code}: {response.text}")
                return article.get("content", "")

        except Exception as e:
            print(f"❌ Exception during cleaning content: {e}")
            return article.get("content", "")
