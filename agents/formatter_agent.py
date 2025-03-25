from crewai import Agent

class FormatterAgent(Agent):
    def run(self, articles):
        for article in articles:
            article["final_html"] = f"<h1>{article['title']}</h1>\n{article['translated_html']}"
        return articles
