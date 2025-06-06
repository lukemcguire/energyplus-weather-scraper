"""Main entry point script for the EnergyPlus weather scraper application.

This script orchestrates the entire scraping process. It sets up logging,
initializes the scraper, starts the crawl, handles overall execution flow,
and triggers the saving of results to a CSV file upon completion.
"""

import logging
import sys

from src.config import OUTPUT_CSV_FILENAME
from src.scraper import scrape
from src.utils import locations_to_csv


def setup_logging() -> logging.Logger:
    """Configures logging to file and console.

    Returns:
        A logger associated with main.py
    """
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
    root_logger = logging.getLogger()  # Get the root logger
    root_logger.setLevel(logging.INFO)  # Set minimum level to capture

    # File Handler
    file_handler = logging.FileHandler("scraper.log", mode="w")  # 'w' overwrites log each run
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    # main logger
    logger = logging.getLogger(__name__)
    logger.info("Logging configured.")  # Log that logging is set up
    return logger


def main() -> None:
    """Make a jazz noise here."""
    logger = setup_logging()
    logger.info("Starting EnergyPlus weather scraper...")

    try:
        final_locations = scrape()

        if final_locations:
            logger.info("Scraping complete. Found %d unique locations.", len(final_locations))
            locations_to_csv(final_locations, OUTPUT_CSV_FILENAME)
            logger.info("Data saved to %s", OUTPUT_CSV_FILENAME)
        else:
            logger.warning("Scraping finished, but no locations were collected.")

    except Exception:
        logger.exception("An unhandled error stopped the scraper!")
    finally:
        logger.info("Scraper finished.")


if __name__ == "__main__":
    main()
