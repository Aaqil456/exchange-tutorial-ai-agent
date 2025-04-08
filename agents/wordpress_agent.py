import os
import requests
import base64
import time
import json
from .base_agent import BaseAgent  # Ensure base_agent.py exists in the same package
from .translator_agent import TranslatorAgent  # Import TranslatorAgent from translator_agent.py

# === ENV VARIABLES (from GitHub Secrets or OS) ===
WP_URL = os.getenv("WP_URL", "https://teknologiblockchain.com/wp-json/wp/v2")
WP_USER = os.getenv("WP_USER")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
PANDUAN_CATEGORY_ID = 1395  # Category ID for 'Panduan'

class WordPressAgent(BaseAgent):
    def run(self, articles):
        print("🚀 Posting to WordPress (drafts under Panduan category)...")
        print(f"[DEBUG] WP_URL: {WP_URL}")
        print(f"[DEBUG] WP_USER: {'✅ Loaded' if WP_USER else '❌ Not Set'}")
        print(f"[DEBUG] WP_APP_PASSWORD: {'✅ Loaded' if WP_APP_PASSWORD else '❌ Not Set'}")

        if not WP_USER or not WP_APP_PASSWORD:
            print("❌ ERROR: WordPress credentials are missing. Make sure GitHub Secrets are passed correctly.")
            return

        # 🔐 Quick credential check
        self._test_wp_auth()

        # Instantiate TranslatorAgent
        translator_agent = TranslatorAgent()

        posted_count = 0
        for article in articles:
            # First, translate the title and content
            translated_articles = translator_agent.run([article])
            translated_article = translated_articles[0]  # Since we passed a list of 1 article

            translated_title = translated_article.get("translated_title", translated_article.get("title"))
            translated_content = translated_article.get("translated_html", translated_article.get("content"))

            print(f"\n📄 Posting article: {translated_title}")
            image_url = article.get("image", "")
            original_url = article.get("url", "")

            media_id, uploaded_image_url = self.upload_image_to_wp(image_url)

            success = self.post_to_wp(translated_title, translated_content, original_url, uploaded_image_url, media_id)

            if success:
                posted_count += 1
                print(f"✅ Draft saved: {translated_title}")
            else:
                print(f"❌ Failed to post: {translated_title}")

            time.sleep(1)

        print(f"\n📝 Total drafts posted: {posted_count}")
        return articles

    def _test_wp_auth(self):
        credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
        token = base64.b64encode(credentials.encode()).decode()
        headers = {"Authorization": f"Basic {token}"}
        test_url = f"{WP_URL}/posts"
        try:
            resp = requests.get(test_url, headers=headers)
            print(f"[DEBUG] Auth Test Status: {resp.status_code}")
            print(f"[DEBUG] Auth Test Response: {resp.text}")
        except Exception as e:
            print(f"[Auth Test Exception] {e}")

    def post_to_wp(self, title, content, original_url, uploaded_image_url=None, media_id=None):
        credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
        token = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json"
        }

        image_html = f"<img src='{uploaded_image_url}' alt='{title}'/><br>" if uploaded_image_url else ""
        full_content = (
            f"<h1>{title}</h1><br>"
            f"{image_html}"
            f"{content}"
            f"<p>📌 Baca artikel asal di sini: <a href='{original_url}'>{original_url}</a></p>"
        )

        post_data = {
            "title": title,
            "content": full_content,
            "status": "private",
            "categories": [PANDUAN_CATEGORY_ID]
        }

        if media_id:
            post_data["featured_media"] = media_id
            time.sleep(1)

        print(f"[DEBUG] Posting to WordPress with payload:\n{json.dumps(post_data, indent=2)}")
        print(f"[DEBUG] Headers:\n{headers}")

        try:
            response = requests.post(f"{WP_URL}/posts", headers=headers, json=post_data)
            print(f"[DEBUG] WP Response Status: {response.status_code}")
            print(f"[DEBUG] WP Response Body: {response.text}")

            return response.status_code == 201
        except Exception as e:
            print(f"[Post Exception] {e}")
            return False

    def upload_image_to_wp(self, image_url):
        if not image_url:
            print("[Upload Skipped] No image URL provided.")
            return None, None

        try:
            img_response = requests.get(image_url, headers={"User-Agent": "Mozilla/5.0"})
            if img_response.status_code != 200:
                print(f"[Image Download Error] Status {img_response.status_code}")
                return None, None
            image_data = img_response.content
        except Exception as e:
            print(f"[Image Download Exception] {e}")
            return None, None

        credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
        token = base64.b64encode(credentials.encode()).decode()
        file_name = image_url.split("/")[-1] or "image.jpg"

        headers = {
            "Authorization": f"Basic {token}",
            "Content-Disposition": f"attachment; filename={file_name}",
            "Content-Type": "image/jpeg"
        }

        try:
            response = requests.post(f"{WP_URL}/media", headers=headers, data=image_data)
            if response.status_code == 201:
                media = response.json()
                print(f"[DEBUG] Image uploaded: {media.get('source_url')}")
                return media.get("id"), media.get("source_url")
            else:
                print(f"[Upload Error] {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[Upload Exception] {e}")

        return None, None
