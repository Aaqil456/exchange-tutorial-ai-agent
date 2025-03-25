from crewai import Agent
import json
from datetime import datetime

class SaverAgent(Agent):
    def run(self, articles):
        with open("mexc_translated_articles.json", "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "articles": articles
            }, f, ensure_ascii=False, indent=4)
        print("✅ Saved JSON")
