import sys
import os

# Add root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.scraper_agent import ScraperAgent
from agents.cleaner_agent import CleanerAgent
from agents.image_validator import ImageValidator
from agents.translator_agent import TranslatorAgent
from agents.formatter_agent import FormatterAgent
from agents.validator_agent import ValidatorAgent
from agents.saver_agent import SaverAgent
from agents.render_agent import RenderAgent  # ✅ Added RenderAgent import
from agents.wordpress_agent import WordPressAgent

def main():
    # Agent: Scraper
    scraper = ScraperAgent(
        role="Web Scraper",
        goal="Scrape tutorials with all content and images intact.",
        backstory="You are responsible for getting clean and complete tutorial content from the MEXC trading guide page."
    )

    # Agent: Cleaner
    cleaner = CleanerAgent(
        role="Content Cleaner",
        goal="Filter and clean the scraped articles, removing anything irrelevant.",
        backstory="You ensure only high-quality tutorial articles proceed to translation."
    )

    # Agent: Image Validator
    image_validator = ImageValidator(
        role="Image Validator",
        goal="Check that each article includes embedded images in the correct positions.",
        backstory="You double-check every piece of content to ensure images are in place."
    )

    # Agent: Translator
    translator = TranslatorAgent(
        role="Translator",
        goal="Translate text content to Malay without altering structure or images.",
        backstory="You are a careful translator that preserves structure and converts only text."
    )

    # Agent: Formatter
    formatter = FormatterAgent(
        role="Formatter",
        goal="Format the translated content into a professional tutorial layout.",
        backstory="You ensure everything looks beautiful, with clear headings, images, and structure."
    )

    # ✅ Agent: Render Agent
    renderer = RenderAgent(
        role="Renderer",
        goal="Render the translated tutorials into final structured HTML with images in correct positions.",
        backstory="You take the translated and formatted content and create final HTML output for display."
    )

    # Agent: Output Validator
    validator = ValidatorAgent(
        role="Output Validator",
        goal="Perform final validation to ensure quality and correctness.",
        backstory="You are the final checkpoint for quality assurance."
    )

    wordpress = WordPressAgent(
        role="WordPress Publisher",
        goal="Post articles to WordPress as drafts under the Panduan category.",
        backstory="You help publish tutorials to WordPress in an organized, safe manner."
    )

    # ... before saver.run(...)
    wordpress.run(final_validated)

    # Agent: Saver
    saver = SaverAgent(
        role="Saver",
        goal="Save validated and rendered articles into a JSON file.",
        backstory="You safely store the final tutorial collection for publishing."
    )

    print("Scraping articles...")
    articles = scraper.run()

    print("Cleaning articles...")
    cleaned_articles = cleaner.run(articles)

    print("Validating images...")
    validated_articles = image_validator.run(cleaned_articles)

    print("Translating articles...")
    translated_articles = translator.run(validated_articles)

    print("Formatting articles...")
    formatted_articles = formatter.run(translated_articles)

    print("Rendering articles into final HTML...")
    rendered_articles = renderer.run(formatted_articles)  # ✅ New render step

    print("Validating final output...")
    final_validated = validator.run(rendered_articles)

    print("Saving to JSON...")
    saver.run(final_validated)

    print("Process completed successfully!")

if __name__ == "__main__":
    main()
