import os
import requests
import base64
import time
import json
from dotenv import load_dotenv  # ✅ For loading .env variables
from .base_agent import BaseAgent  # ✅ Relative import for class

# === Load environment variables ===
load_dotenv()

WP_URL = os.getenv("WP_URL", "https://teknologiblockchain.com/wp-json/wp/v2")
WP_USER = os.getenv("WP_USER")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
PANDUAN_CATEGORY_ID = 1395  # ✅ Your Panduan category

# === Validate critical env vars ===
if not WP_USER or not WP_APP_PASSWORD:
    print("❌ ERROR: Missing WordPress credentials. Please check your .env file.")
    exit(1)

class WordPressAgent(BaseAgent):
    def run(self, articles):
        print("🚀 Posting to WordPress (drafts under Panduan category)...")
        print(f"[DEBUG] WP_URL: {WP_URL}")
        print(f"[DEBUG] WP_USER: {WP_USER}")
        print(f"[DEBUG] WP_APP_PASSWORD: {'✅ Loaded' if WP_APP_PASSWORD else '❌ Not Loaded'}")

        posted_count = 0

        for article in articles:
            title = article.get("title", "Untitled")
            content = article.get("content", "")
            image_url = article.get("image", "")
            original_url = article.get("url", "")

            print(f"\n📄 Posting article: {title}")
            media_id, uploaded_image_url = self.upload_image_to_wp(image_url)

            print("[DEBUG] Posting to WordPress with payload:")
            success = self.post_to_wp(title, content, original_url, uploaded_image_url, media_id)

            if success:
                posted_count += 1
                print(f"✅ Draft saved: {title}")
            else:
                print(f"❌ Failed to post: {title}")

            time.sleep(1)

        print(f"\n📝 Total drafts posted: {posted_count}")
        return articles

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
            "status": "draft",
            "categories": [PANDUAN_CATEGORY_ID]
        }

        if media_id:
            post_data["featured_media"] = media_id
            time.sleep(1)

        print(f"[DEBUG] Headers:\n{headers}")
        print(f"[DEBUG] WP Payload:\n{json.dumps(post_data, indent=2)}")

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
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8"
            }
            img_response = requests.get(image_url, headers=headers)
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
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "Content-Type": "image/jpeg"
        }

        try:
            media_response = requests.post(
                f"{WP_URL}/media", headers=headers, data=image_data
            )

            if media_response.status_code == 201:
                media_json = media_response.json()
                media_id = media_json.get("id")
                media_url = media_json.get("source_url")
                print(f"✅ Image uploaded: {file_name} (ID: {media_id})")
                return media_id, media_url
            else:
                print(f"[Image Upload Failed] Status: {media_response.status_code}")
                print(media_response.text)
                return None, None
        except Exception as e:
            print(f"[Upload Exception] {e}")
            return None, None
