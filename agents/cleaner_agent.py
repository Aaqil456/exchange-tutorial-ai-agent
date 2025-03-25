from crewai import Agent

class CleanerAgent(Agent):
    def run(self, articles):
        # Optionally filter out short articles or irrelevant links
        return [a for a in articles if len(a["content"]) > 200]
