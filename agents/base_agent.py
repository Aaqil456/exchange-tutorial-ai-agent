class BaseAgent:
    def __init__(self, role, goal, backstory):
        self.role = role
        self.goal = goal
        self.backstory = backstory

    def run(self, *args, **kwargs):
        raise NotImplementedError("Each agent must implement its own run method.")
