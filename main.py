from crewai import Crew

def main():
    crew = Crew.from_yaml("crew.yaml")
    crew.run()

if __name__ == "__main__":
    main()
