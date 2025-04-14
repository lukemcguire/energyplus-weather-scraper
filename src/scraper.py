"""Core web scraping and crawling logic for the EnergyPlus weather site.

Contains functions responsible for making HTTP requests to fetch web pages
and EPW file headers, implementing polite delays and retries. Also includes
the main recursive crawling algorithm to navigate the site structure and
discover weather data files.
"""

import logging

import requests

# Get a logger named after this module (e.g., 'src.scraper')
logger = logging.getLogger(__name__)


def crawl(url_queue: list[str], visited: set[str]) -> dict[str, dict]:  # type: ignore[empty-body]
    """Main web crawl logic."""
    ...


def fetch_url(url: str) -> requests.Response | None:
    """Fetch url from page."""
    ...


def fetch_epw_header(epw_file_url: str) -> requests.Response:  # type: ignore[empty-body]
    """Fetch epw header."""
    ...
