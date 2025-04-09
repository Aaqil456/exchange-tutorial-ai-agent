import requests
import os
import time
from .base_agent import BaseAgent  # Correct import from local agent base class

class TranslatorAgent(BaseAgent):  # Subclassing your own BaseAgent
    def __init__(self, role, goal, backstory):
        super().__init__(role, goal, backstory)

    def run(self, articles):
        GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
        translated_articles = []

        for article in articles:
            # Prompt for title
            title_prompt = (
                "Translate the following title into Malay (Bahasa Malaysia).\n"
                "Only return the translated text without any explanation.\n"
                "Use natural, conversational, friendly Malaysian Malay — like how a friend shares info.\n"
                "Keep it simple, relaxed, and easy to understand.\n"
                "Avoid using exaggerated slang words or interjections (such as \"Eh,\" \"Korang,\" \"Woi,\" \"Wooohooo,\" \"Wooo,\" or anything similar).\n"
                "No shouting words or unnecessary excitement.\n"
                "Keep it informative, approachable, and casual — but clean and neutral.\n"
                "Do not use emojis unless they appear in the original text.\n"
                "Do not translate brand names or product names.\n\n"
                f"{article['title']}"
            )

            # Prompt for content
            content_prompt = (
                "Translate the following tutorial content into Malay (Bahasa Malaysia).\n"
                "Only return the translated text without any explanation.\n"
                "Use natural, conversational, friendly Malaysian Malay — like how a friend shares info.\n"
                "Keep it simple, relaxed, and easy to understand.\n"
                "Avoid using exaggerated slang words or interjections (such as \"Eh,\" \"Korang,\" \"Woi,\" \"Wooohooo,\" \"Wooo,\" or anything similar).\n"
                "No shouting words or unnecessary excitement.\n"
                "Keep it informative, approachable, and casual — but clean and neutral.\n"
                "Do not use emojis unless they appear in the original text.\n"
                "Do not translate brand names or product names.\n"
                "Maintain the structure and do not alter the position of images (already embedded as <img> tags).\n"
                "Translate all text content but do not translate anything inside <img> tags.\n\n"
                f"{article['content']}"
            )

            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
            headers = {"Content-Type": "application/json"}

            # Translate title
            title_payload = {"contents": [{"parts": [{"text": title_prompt}]}]}
            for attempt in range(3):
                try:
                    response = requests.post(gemini_url, headers=headers, json=title_payload)
                    if response.status_code == 200:
                        translated_title = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        article["translated_title"] = translated_title
                        break
                    time.sleep(2)
                except Exception as e:
                    print(f"[Title Translation Error] {e}")

            # Translate content
            content_payload = {"contents": [{"parts": [{"text": content_prompt}]}]}
            for attempt in range(3):
                try:
                    response = requests.post(gemini_url, headers=headers, json=content_payload)
                    if response.status_code == 200:
                        translated_content = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        article["translated_html"] = translated_content
                        break
                    time.sleep(2)
                except Exception as e:
                    print(f"[Content Translation Error] {e}")

            translated_articles.append(article)

        return translated_articles
