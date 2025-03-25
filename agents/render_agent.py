from pydantic import BaseModel

class RenderAgent(BaseModel):
    role: str
    goal: str
    backstory: str

    def run(self, articles):
        print("🔎 Rendering articles into final HTML structure...")
        rendered_articles = []

        for article in articles:
            rendered_html = f"""
                <h1>{article['title']}</h1>
                <p><a href="{article['url']}">Original Article Link</a></p>
                {article['translated_html']}
            """
            article['final_html'] = rendered_html
            rendered_articles.append(article)

        print(f"✅ Rendered {len(rendered_articles)} articles.")
        return rendered_articles
