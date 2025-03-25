from crewai import Agent

class ImageValidator(Agent):
    def run(self, articles):
        # Ensure each article has at least one image
        validated = [a for a in articles if '<img' in a["content"]]
        return validated
