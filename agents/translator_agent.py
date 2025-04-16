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
                "Translate and rewrite the following HTML tutorial article from English to Bahasa Malaysia.\n\n"
                "Your goal is to create a SEO-optimized, blog-style Bahasa Malaysia article suitable for Malaysian readers.\n\n"
                "DO the following:\n"
                "1. Translate all paragraph content into natural, fluent Bahasa Malaysia — make it sound like a real Malaysian crypto educator.\n"
                "2. Use informal but professional tone (not textbook or robotic).\n"
                "3. Retain the HTML structure, including <h1>, <h2>, <p>, <ul>, <ol>, <li>, <img>. Do NOT modify or translate anything inside <img> tags.\n"
                "4. Keep all crypto and trading terms (e.g., futures, wallet, margin, liquidation) in English inside double quotes.\n"
                "5. Then highlight those double-quoted terms by wrapping them with <strong>. Example: <strong>\"wallet\"</strong>.\n"
                "6. Break long paragraphs into shorter ones for better readability.\n"
                "7. Avoid repeating phrases — write concisely but clearly.\n"
                "8. Translate into Bahasa Malaysia — NOT Bahasa Indonesia. Use 'anda', 'modal', 'untung', 'kerugian', 'dagangan', etc.\n"
                "9. At the end of the article, add a <h2> section titled 'Kesimpulan', and summarize the key points in 2–4 bullet points using <ul><li>.\n"
                "\n"
                "DO NOT:\n"
                "- Do not return explanation or metadata.\n"
                "- Do not use Bahasa Indonesia.\n"
                "- Do not use repetitive corporate tones or salesy lines.\n"
                "\n"
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
