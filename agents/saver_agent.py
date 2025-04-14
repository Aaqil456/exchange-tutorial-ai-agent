from crewai import Agent
import json
from datetime import datetime
import os

class SaverAgent(Agent):
    def run(self, articles):
        filename = "translated_articles.json"
        all_articles = []

        # ✅ Load existing if file exists
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                    all_articles = existing_data.get("articles", [])
                except Exception as e:
                    print(f"⚠️ Failed to load existing file: {e}")

        # ✅ Add new ones with timestamp
        for article in articles:
            article["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            all_articles.append(article)

        # ✅ Save all into same file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "articles": all_articles
            }, f, ensure_ascii=False, indent=4)

        print(f"✅ Appended & saved {len(articles)} new articles to {filename}")
