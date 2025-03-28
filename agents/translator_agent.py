from crewai import Agent
import requests
import os
import time

class TranslatorAgent(Agent):
    def run(self, articles):
        GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
        translated_articles = []

        for article in articles:
            prompt = (
                "Translate the following tutorial content from English to Malay (Bahasa Malaysia). "
                "the translation should have the tone of natural kolokial malay malaysian. Make it conversational, simple, friendly, like how a friend shares info — but no over-the-top slang or yelling words."
                "Maintain the structure and do not alter the position of images (already embedded as <img> tags). "
                "Translate all text content but do not translate anything inside <img> tags.\n\n"
                f"{article['content']}"
            )

            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
            headers = {"Content-Type": "application/json"}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}

            for attempt in range(3):
                response = requests.post(gemini_url, headers=headers, json=payload)
                if response.status_code == 200:
                    translated = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    article["translated_html"] = translated
                    break
                time.sleep(2)

            translated_articles.append(article)

        return translated_articles
