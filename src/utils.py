"""General utility functions supporting the weather scraper application.

This module holds helper functions that don't belong to a more specific
module like parsing or scraping. Currently, its primary role is likely
to handle the writing of the final collected data to a CSV file.
"""


def locations_to_csv(locations: dict[str, dict], output_filename: str) -> None:
    """Write all locations to csv file."""
    ...
