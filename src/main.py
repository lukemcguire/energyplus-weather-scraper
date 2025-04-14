"""Main entry point script for the EnergyPlus weather scraper application.

This script orchestrates the entire scraping process. It sets up logging,
initializes the scraper, starts the crawl, handles overall execution flow,
and triggers the saving of results to a CSV file upon completion.
"""

import logging
import sys

from src.config import BASE_URL, OUTPUT_CSV_FILENAME
from src.scraper import crawl
from src.utils import locations_to_csv


def setup_logging() -> None:
    """Configures logging to file and console."""
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

    logging.info("Logging configured.")  # Log that logging is set up


def main() -> None:
    """Make a jazz noise here."""
    setup_logging()
    logging.info("Starting EnergyPlus weather scraper...")

    visited_urls: set[str] = set()
    url_queue = [BASE_URL]  # Start with the base URL

    try:
        final_locations = crawl(url_queue, visited_urls)  # Assuming crawl manages queue/visited

        if final_locations:
            logging.info(f"Scraping complete. Found {len(final_locations)} unique locations.")
            locations_to_csv(final_locations, OUTPUT_CSV_FILENAME)
            logging.info(f"Data saved to {OUTPUT_CSV_FILENAME}")
        else:
            logging.warning("Scraping finished, but no locations were collected.")

    except Exception:
        logging.critical("An unhandled error stopped the scraper!", exc_info=True)
    finally:
        logging.info("Scraper finished.")


if __name__ == "__main__":
    main()
