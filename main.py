from agents.scraper_agent import ScraperAgent
from agents.cleaner_agent import CleanerAgent
from agents.image_validator import ImageValidator
from agents.translator_agent import TranslatorAgent
from agents.formatter_agent import FormatterAgent
from agents.validator_agent import ValidatorAgent
from agents.saver_agent import SaverAgent

def main():
    scraper = ScraperAgent(
        role="Web Scraper",
        goal="Scrape tutorials with all content and images intact.",
        backstory="You are responsible for getting clean and complete tutorial content from the MEXC trading guide page."
    )
    cleaner = CleanerAgent(
        role="Content Cleaner",
        goal="Filter and clean the scraped articles, removing anything irrelevant.",
        backstory="You ensure only high-quality tutorial articles proceed to translation."
    )
    image_validator = ImageValidator(
        role="Image Validator",
        goal="Check that each article includes embedded images in the correct positions.",
        backstory="You double-check every piece of content to ensure images are in place."
    )
    translator = TranslatorAgent(
        role="Translator",
        goal="Translate text content to Malay without altering structure or images.",
        backstory="You are a careful translator that preserves structure and converts only text."
    )
    formatter = FormatterAgent(
        role="Formatter",
        goal="Format the translated content into a professional tutorial layout.",
        backstory="You ensure everything looks beautiful, with clear headings, images, and structure."
    )
    validator = ValidatorAgent(
        role="Output Validator",
        goal="Perform final validation to ensure quality and correctness.",
        backstory="You are the final checkpoint for quality assurance."
    )
    saver = SaverAgent(
        role="Saver",
        goal="Save validated articles into a JSON file.",
        backstory="You safely store the final tutorial collection for publishing."
    )

    articles = scraper.run()
    cleaned_articles = cleaner.run(articles)
    validated_articles = image_validator.run(cleaned_articles)
    translated_articles = translator.run(validated_articles)
    formatted_articles = formatter.run(translated_articles)
    final_validated = validator.run(formatted_articles)
    saver.run(final_validated)

if __name__ == "__main__":
    main()
