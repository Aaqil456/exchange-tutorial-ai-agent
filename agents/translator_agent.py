from crewai import Agent
import requests
import os
import time
from .base_agent import BaseAgent  # Ensure this import is correct

class TranslatorAgent(BaseAgent):  # Now inheriting from BaseAgent
    def __init__(self, role, goal, backstory):
        super().__init__(role, goal, backstory)  # Initialize with BaseAgent's constructor
    
    def run(self, articles):
        GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
        translated_articles = []

        for article in articles:
            # Translate the title first
            title_prompt = (
                "Translate the following title into Malay (Bahasa Malaysia). "
                "The translation should have the tone of natural colloquial Malaysian Malay. "
                "Keep it simple, friendly, and conversational, but avoid over-the-top slang or shouting words.\n\n"
                f"{article['title']}"
            )

            # Translate the content
            content_prompt = (
                "Translate the following tutorial content into Malay (Bahasa Malaysia). "
                "The translation should have the tone of natural colloquial Malaysian Malay. "
                "Make it conversational, simple, friendly, like how a friend shares info — but no over-the-top slang or yelling words."
                "Maintain the structure and do not alter the position of images (already embedded as <img> tags). "
                "Translate all text content but do not translate anything inside <img> tags.\n\n"
                f"{article['content']}"
            )

            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
            headers = {"Content-Type": "application/json"}
            
            # Translate title
            title_payload = {"contents": [{"parts": [{"text": title_prompt}]}]}
            
            # Translate content
            content_payload = {"contents": [{"parts": [{"text": content_prompt}]}]}

            # Attempt translation for title and content (3 retries for both)
            for attempt in range(3):
                try:
                    # Request to translate the title
                    title_response = requests.post(gemini_url, headers=headers, json=title_payload)
                    if title_response.status_code == 200:
                        translated_title = title_response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        article["translated_title"] = translated_title
                        break
                    time.sleep(2)
                except Exception as e:
                    print(f"[Title Translation Error] {e}")
            
            # Translate content
            for attempt in range(3):
                try:
                    content_response = requests.post(gemini_url, headers=headers, json=content_payload)
                    if content_response.status_code == 200:
                        translated_content = content_response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        article["translated_html"] = translated_content
                        break
                    time.sleep(2)
                except Exception as e:
                    print(f"[Content Translation Error] {e}")

            translated_articles.append(article)

        return translated_articles
