import requests
import os
import time
from .base_agent import BaseAgent  # Import base class

class TranslatorAgent(BaseAgent):
    def __init__(self, role, goal, backstory):
        super().__init__(role, goal, backstory)

    def run(self, articles):
        GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

        print("🔑 GEMINI_API_KEY status:", "✅ OK" if GOOGLE_API_KEY else "❌ MISSING")
        if not GOOGLE_API_KEY:
            print("❌ Translation skipped. No API key found.")
            return articles

        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}"
        headers = {"Content-Type": "application/json"}
        translated_articles = []

        for article in articles:
            print(f"\n🔄 Translating article: {article.get('title')[:60]}...")

            # --- Translate Title ---
            title_prompt = (
                "Translate the following title into Malay (Bahasa Malaysia)  and make it SEO optimized title without changing the meaning.\n"
                "Only return the translated text without any explanation. Maintain crypto and trading topic related word in english in double quotes\n"
                "Use natural, conversational, friendly Malaysian Malay — like how a friend shares info.\n"
                "Keep it simple, relaxed, and easy to understand.\n"
                "Avoid using exaggerated slang words or interjections.\n"
                "Do not translate brand names or product names.\n\n"
                f"{article['title']}"
            )

            title_payload = {"contents": [{"parts": [{"text": title_prompt}]}]}
            translated_title = ""

            for attempt in range(3):
                try:
                    response = requests.post(gemini_url, headers=headers, json=title_payload)
                    print("🌐 Gemini Title Response Status:", response.status_code)
                    print("🌐 Gemini Title Response JSON:", response.text[:300])

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
                    time.sleep(2)
                except Exception as e:
                    print(f"❌ Title Translation Exception: {e}")
            
            if not translated_title:
                translated_title = "[Translation failed]"
            print("📝 Translated Title:", translated_title)

            # --- Translate Content ---
            #content_prompt = (
            #    "Translate the following tutorial content into Malay (Bahasa Malaysia). and make it SEO optimized article\n"
            #   "Only return the translated text without any explanation. Maintain crypto and trading topic related word in english in double quotes\n"
            #    "Use natural, conversational, friendly Malaysian Malay — like how a friend shares info.\n"
            #    "Keep it simple, relaxed, and easy to understand.\n"
            #    "Avoid exaggerated slang, emojis, or shouting.\n"
            #    "Maintain HTML structure and <img> tags.\n"
            #    "Do not translate anything inside <img> tags. \n\n"
            #    f"{article['content']}"
            #)

                        # --- Translate Content ---
            content_prompt = (
                "Translate and restructure the following tutorial article from English to Bahasa Malaysia.\n"
                "Preserve the original HTML structure, including all tags such as <h1>, <h2>, <p>, <ul>, <ol>, <li>, and <img>.\n"
                "Do NOT translate any content inside <img> tags, including filenames and alt text.\n"
                "Retain all crypto and trading-related terms in English, and enclose them in double quotes (e.g., \"futures\", \"wallet\", \"liquidation\").\n"
                "Then, highlight these double-quoted terms by wrapping them in <strong> tags for bold formatting — e.g., <strong>\"wallet\"</strong>.\n"
                "Restructure the content to be SEO friendly by using clear headings, proper paragraph breaks, and concise, non-repetitive language.\n"
                "Do NOT include any explanations, comments, or extra notes — only return the translated and formatted HTML content.\n"
                "At the end of the article, add a short summary in Bahasa Malaysia under a <h2> heading titled 'Kesimpulan', highlighting the key points in 2–4 bullet points.\n\n"
                f"{article['content']}"
            )
                        
            content_payload = {"contents": [{"parts": [{"text": content_prompt}]}]}
            translated_content = ""

            for attempt in range(3):
                try:
                    response = requests.post(gemini_url, headers=headers, json=content_payload)
                    print("🌐 Gemini Content Response Status:", response.status_code)
                    print("🌐 Gemini Content Response JSON:", response.text[:300])

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
