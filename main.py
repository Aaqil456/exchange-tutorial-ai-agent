from agents.scraper_agent import ScraperAgent
from agents.cleaner_agent import CleanerAgent
from agents.image_validator import ImageValidator
from agents.translator_agent import TranslatorAgent
from agents.formatter_agent import FormatterAgent
from agents.validator_agent import ValidatorAgent
from agents.saver_agent import SaverAgent

def main():
    # Step 1: Scrape
    scraper = ScraperAgent()
    articles = scraper.run()

    # Step 2: Clean
    cleaner = CleanerAgent()
    cleaned_articles = cleaner.run(articles)

    # Step 3: Validate Images
    validator_img = ImageValidator()
    validated_articles = validator_img.run(cleaned_articles)

    # Step 4: Translate
    translator = TranslatorAgent()
    translated_articles = translator.run(validated_articles)

    # Step 5: Format
    formatter = FormatterAgent()
    formatted_articles = formatter.run(translated_articles)

    # Step 6: Final Validation
    final_validator = ValidatorAgent()
    final_validated = final_validator.run(formatted_articles)

    # Step 7: Save
    saver = SaverAgent()
    saver.run(final_validated)

if __name__ == "__main__":
    main()
