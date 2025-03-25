from crewai import Agent

class ValidatorAgent(Agent):
    def run(self, articles):
        validated = []
        for a in articles:
            if "final_html" in a and "<img" in a["final_html"]:
                validated.append(a)
        return validated
