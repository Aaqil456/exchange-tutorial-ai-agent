import requests
import os
import time
from .base_agent import BaseAgent  # Correct import from local agent base class

class TranslatorAgent(BaseAgent):  # Subclassing your own BaseAgent
    def __init__(self, role, goal, backstory):
        super().__init__(role, goal, backstory)

    def run(self, articles):
    GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

    if not GOOGLE_API_KEY:
        print("❌ GEMINI_API_KEY is not set. Translation will fail.")
        return articles

    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    translated_articles = []

    for article in articles:
        print(f"\n🔄 Translating article: {article.get('title')[:60]}...")

        # --- Translate Title ---
        title_prompt = (
            "Translate the following title into Malay (Bahasa Malaysia).\n"
            "Only return the translated text without any explanation.\n"
            "Use natural, conversational, friendly Malaysian Malay...\n\n"
            f"{article['title']}"
        )

        title_payload = {"contents": [{"parts": [{"text": title_prompt}]}]}
        translated_title = ""

        for attempt in range(3):
            try:
                response = requests.post(gemini_url, headers=headers, json=title_payload)
                if response.status_code == 200:
                    translated_title = (
                        response.json()
                        .get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "")
                        .strip()
                    )
                    break
                else:
                    print(f"⚠️ Title Translation failed [Attempt {attempt+1}] - Status: {response.status_code}")
                    print(response.text)
                time.sleep(2)
            except Exception as e:
                print(f"❌ Title Translation Exception: {e}")
        
        if not translated_title:
            translated_title = "[Translation failed]"
        
        print("📝 Translated Title:", translated_title)

        # --- Translate Content ---
        content_prompt = (
            "Translate the following tutorial content into Malay (Bahasa Malaysia).\n"
            "Only return the translated text without any explanation.\n"
            "Keep the structure and <img> tags...\n\n"
            f"{article['content']}"
        )

        content_payload = {"contents": [{"parts": [{"text": content_prompt}]}]}
        translated_content = ""

        for attempt in range(3):
            try:
                response = requests.post(gemini_url, headers=headers, json=content_payload)
                if response.status_code == 200:
                    translated_content = (
                        response.json()
                        .get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "")
                        .strip()
                    )
                    break
                else:
                    print(f"⚠️ Content Translation failed [Attempt {attempt+1}] - Status: {response.status_code}")
                    print(response.text)
                time.sleep(2)
            except Exception as e:
                print(f"❌ Content Translation Exception: {e}")

        if not translated_content:
            translated_content = "[Translation failed]"

        print("📄 Translated Content Preview:\n", translated_content[:300])

        # --- Assign Results ---
        article["translated_title"] = translated_title
        article["translated_html"] = translated_content
        translated_articles.append(article)

    return translated_articles
