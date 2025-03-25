import json
from datetime import datetime
from crewai import Agent

class RenderAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self):
        print("📜 Rendering final HTML for articles...")

        with open("mexc_translated_articles.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        for article in data["articles"]:
            translated_html = article.get("translated_html", "")
            if not translated_html or translated_html == "Translation failed":
                print(f"⚠️ Skipping {article['title']} due to missing translation.")
                continue

            # Generate final HTML structure
            final_html = f"""
            <article>
                <h1>{article['title']}</h1>
                <p><strong>Breadcrumbs:</strong> {article.get('breadcrumbs', '')}</p>
                <div class="tutorial-content">
                    {translated_html}
                </div>
            </article>
            """
            article["final_html"] = final_html.strip()

        # Save back to JSON
        data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("mexc_translated_articles.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print("✅ Rendered final HTML for all articles.")

