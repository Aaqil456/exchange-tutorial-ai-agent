import os
import requests
import base64
import time
import json
from .base_agent import BaseAgent  # ✅ Use relative import

# === ENV VARIABLES ===
WP_URL = os.getenv("WP_URL", "https://teknologiblockchain.com/wp-json/wp/v2")
WP_USER = os.getenv("WP_USER")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
PANDUAN_CATEGORY_ID = 1395  # ✅ Confirmed category ID for Panduan

class WordPressAgent(BaseAgent):
    def run(self, articles):
        print("🚀 Posting to WordPress (drafts under Panduan category)...")
        posted_count = 0

        for article in articles:
            title = article.get("title", "Untitled")
            content = article.get("content", "")
            image_url = article.get("image", "")
            original_url = article.get("url", "")

            media_id, uploaded_image_url = self.upload_image_to_wp(image_url)
            success = self.post_to_wp(title, content, original_url, uploaded_image_url, media_id)

            if success:
                posted_count += 1
                print(f"✅ Draft saved: {title}")
            else:
                print(f"❌ Failed to post: {title}")

            time.sleep(1)

        print(f"📝 Total drafts posted: {posted_count}")
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
            "status": "publish",  # ✅ Post as draft
            "categories": [PANDUAN_CATEGORY_ID]
        }

        if media_id:
            post_data["featured_media"] = media_id
            time.sleep(1)

        try:
            response = requests.post(f"{WP_URL}/posts", headers=headers, json=post_data)

            if response.status_code == 201:
                return True
            else:
                print(f"❌ Failed to post article '{title}'")
                print(f"📡 Status Code: {response.status_code}")
                print(f"📄 Response: {response.text}")
                print(f"📦 Payload: {json.dumps(post_data, indent=2)}")
                return False

        except Exception as e:
            print(f"[Post Exception] {e}")
            return False

    def upload_image_to_wp(self, image_url):
        if not image_url:
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

        media_endpoint = f"{WP_URL}/media"
        credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
        token = base64.b64encode(credentials.encode()).decode()
        file_name = image_url.split("/")[-1] or "image.jpg"

        headers = {
            "Authorization": f"Basic {token}",
            "Content-Disposition": f"attachment; filename={file_name}",
            "Content-Type": "image/jpeg",
        }

        try:
            upload_response = requests.post(media_endpoint, headers=headers, data=image_data)
            if upload_response.status_code == 201:
                media_data = upload_response.json()
                return media_data.get("id"), media_data.get("source_url")
            else:
                print(f"[Image Upload Failed] Status: {upload_response.status_code}")
                print(f"🪵 Response: {upload_response.text}")
        except Exception as e:
            print(f"[Image Upload Exception] {e}")

        return None, None
