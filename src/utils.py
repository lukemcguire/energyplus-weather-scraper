"""General utility functions supporting the weather scraper application.

This module holds helper functions that don't belong to a more specific
module like parsing or scraping. Currently, its only role is to handle the
writing of the final collected data to a CSV file and to create a random delay
for polite scraping.
"""

import csv
import logging
import random
import time
from pathlib import Path

from src.config import ALL_FIELD_NAMES, MAX_DELAY, MIN_DELAY

logger = logging.getLogger(__name__)


def locations_to_csv(locations: dict[str, dict], output_filename: str) -> None:
    """Writes the collected location data to a CSV file.

    Creates the output directory if it doesn't exist. Writes the values
    (location dictionaries) from the input dictionary to the specified CSV file
    using the fieldnames defined in the configuration.

    Args:
        locations: The dictionary containing the final processed location data,
                   keyed by WMO index.
        output_filename: The name for the output CSV file (e.g., 'locations.csv').
    """
    if not locations:
        logger.warning("No locations provided to write to CSV. Skipping.")
        return

    output_dir = Path("output/")
    output_path = output_dir / output_filename

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Ensured output directory exists: %s", output_dir)
        logger.info("Attempting to write %d locations to CSV: %s", len(locations), output_path)

        with Path(output_path).open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=ALL_FIELD_NAMES, extrasaction="ignore")

            writer.writeheader()
            for location_data in locations.values():
                writer.writerow(location_data)

        logger.info("Successfully wrote %d locations to %s", len(locations), output_path)

    except OSError:
        logger.exception("Error writing to CSV file %s: %s", output_path)
    except csv.Error:
        logger.exception("CSV specific error writing to %s: %s", output_path)
    except Exception:
        logger.exception("Unexpected error writing locations to CSV %s: %s", output_path)


def random_delay(min_delay: float = MIN_DELAY, max_delay: float = MAX_DELAY) -> None:
    """Pauses execution for a random duration between min_delay and max_delay.

    Used to introduce delays between network requests for polite scraping.
    Reads default delay bounds from configuration.

    Args:
        min_delay: The minimum delay in seconds.
        max_delay: The maximum delay in seconds.
    """
    # Initialize delay
    delay: float = 0
    # Ensure min_delay is not greater than max_delay
    if min_delay > max_delay:
        # Swap them if they are inverted
        min_delay, max_delay = max_delay, min_delay
        logger.warning("min_delay (%f) was greater than max_delay (%f), swapping.", max_delay, min_delay)
    elif min_delay == max_delay:
        delay = min_delay  # Use fixed delay if min == max
    else:
        delay = random.uniform(min_delay, max_delay)

    logger.debug("Sleeping for %.2f seconds...", delay)
    time.sleep(delay)
