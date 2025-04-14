from crewai import Agent

class ImageValidator(Agent):
    def run(self, articles):
        validated = []

        for a in articles:
            if '<img' not in a["content"]:
                print(f"⚠️ No image found in: {a['title']}")
            else:
                print(f"🖼️ Image detected in: {a['title']}")
            validated.append(a)

        print(f"✅ Total articles passed: {len(validated)}")
        return validated
