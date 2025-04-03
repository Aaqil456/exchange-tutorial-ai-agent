import os
import requests
from agents.base_agent import BaseAgent

WORDPRESS_URL = os.environ.get("WORDPRESS_URL")
WORDPRESS_USER = os.environ.get("WORDPRESS_USER")
WORDPRESS_APP_PASS = os.environ.get("WORDPRESS_APP_PASS")

class WordPressAgent(BaseAgent):
    def run(self, articles):
        print("📝 Posting to WordPress as drafts...")

        for article in articles:
            post_data = {
                "title": article.get("title", "Untitled"),
                "content": article.get("content", ""),
                "status": "draft",  # 🔒 Save as draft
                "categories": self.get_category_id("Panduan"),
            }

            response = requests.post(
                f"{WORDPRESS_URL}/wp-json/wp/v2/posts",
                auth=(WORDPRESS_USER, WORDPRESS_APP_PASS),
                headers={"Content-Type": "application/json"},
                json=post_data
            )

            if response.status_code == 201:
                print(f"✅ Draft saved: {article['title']}")
            else:
                print(f"❌ Failed to save draft: {article['title']}")
                print(response.status_code, response.text)

    def get_category_id(self, category_name):
        try:
            response = requests.get(
                f"{WORDPRESS_URL}/wp-json/wp/v2/categories",
                auth=(WORDPRESS_USER, WORDPRESS_APP_PASS),
                params={"search": category_name}
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    return data[0]["id"]
            print(f"⚠️ Category '{category_name}' not found.")
            return None
        except Exception as e:
            print(f"⚠️ Category lookup failed: {e}")
            return None
