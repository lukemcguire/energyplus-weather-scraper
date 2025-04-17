"""Core web scraping and crawling logic for the EnergyPlus weather site.

Contains functions responsible for making HTTP requests to fetch GeoJSON,
extracting EPW URLs, and processing them to get the EPW file headers,
implementing polite delays and retries. Utilizes partial requests where possible
to avoid downloading more of the file than is necessary.
"""

import json
import logging
import time

import requests
from bs4 import BeautifulSoup

from src.config import GEOJSON_URL, MAX_RETRIES, REQUEST_DELAY, SOURCE_PRIORITY
from src.data_handler import add_location
from src.parser import extract_epw_location_line, parse_epw_location_line

# Get a logger named after this module (e.g., 'src.scraper')
logger = logging.getLogger(__name__)


def scrape() -> dict[str, dict]:
    """Main web scraping logic.

    Returns:
        A dictionary of dictionaries containing the parsed location, weather
        station, and weather file data.
    """
    logger.info(f"Begin scrape of {GEOJSON_URL} ...")
    locations = _fetch_geojson(GEOJSON_URL)
    urls = _get_epw_file_urls(locations)
    processed_locations: dict[str, dict] = {}
    successfully_processed = 0

    for i, url in enumerate(urls):
        epw_header: bytes | None = None
        retries = 0
        logger.debug(f"Attempting to download epw file data from {url}")
        while epw_header is None and retries < MAX_RETRIES:
            if retries > 0:
                logger.info("Download attempt failed for %s - Retrying...", url)
            epw_header = _fetch_epw_header(url)
            retries += 1
            time.sleep(REQUEST_DELAY)

        if epw_header is None:
            logger.error("Unable to download EPW header information from URL : %s", url)
            continue

        first_line = extract_epw_location_line(epw_header, url)

        if first_line is None:
            # Error logging already occurred in extract_epw_location_line
            continue

        try:
            new_location = parse_epw_location_line(first_line)
        except ValueError as e:
            logger.error("Error processing %s : %s", url, e)
            continue

        add_location(new_location, processed_locations, SOURCE_PRIORITY)
        successfully_processed += 1
        if successfully_processed % 50 == 0:
            logger.info("Processed %d URLs with %d failures.", successfully_processed, i + 1 - successfully_processed)
            logger.info("Processed %d unique locations so far.", len(processed_locations))

    logger.info(
        "Processed %d / %d URLs for a total of %d unique locations.",
        successfully_processed,
        len(locations),
        len(processed_locations),
    )

    return processed_locations


def _fetch_geojson(url: str) -> list[dict]:
    """Fetches and parses a GeoJSON file, returning its 'features' list.

    Attempts to retrieve JSON data from the specified URL. If successful,
    extracts the list associated with the 'features' key. Handles network,
    HTTP, and JSON parsing errors gracefully by logging them and returning
    an empty list.

    Args:
        url: The URL of the GeoJSON file.

    Returns:
        A list of GeoJSON feature dictionaries found under the 'features' key,
        or an empty list if fetching, parsing, or extraction fails.
    """
    locations = []
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        data = response.json()
        if isinstance(data, dict):
            locations = data.get("features", [])
            if not isinstance(locations, list):
                logger.warning(
                    "'features' key in JSON from %s is not a list. Found type: %s",
                    url,
                    type(locations).__name__,
                )
                locations = []
        else:
            logger.warning("JSON response from %s is not a dictionary. Found type: %s", url, type(data).__name__)

        logger.info("Successfully fetched and parsed GeoJSON from %s. Found %d features", url, len(locations))

    except requests.exceptions.RequestException as e:
        logger.error("Request failed for GeoJSON URL %s: %s", url, e)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON from URL %s: %s", url, e)
    except Exception as e:
        logger.error("An unexpected error occurred processing GeoJSON from %s : %s", url, e, exc_info=True)

    return locations


def _get_epw_file_urls(locations: list[dict]) -> list[str]:
    """Extract epw file urls from json.

    Args:
        locations: A list of GeoJSON dictionaries.

    Returns:
        A list of URLs pointing to EPW files.
    """
    urls = []
    logger.info("Attempting to extract urls from %d feature entries.", len(locations))
    for i, location in enumerate(locations):
        properties = location.get("properties", None)
        if not isinstance(properties, dict):
            logger.warning(
                "'properties' key in index %d is not a dictionary. Found type: %s", i, type(properties).__name__
            )
            continue
        anchor = properties.get("epw", "")
        url = _extract_url_from_anchor(anchor)
        if url is not None:
            urls.append(url)

    logger.info("Successfully extracted %d / %d URLs", len(urls), len(locations))

    return urls


def _extract_url_from_anchor(html_snippet: str | None) -> str | None:
    """Parses a string containing an HTML anchor tag and extracts the URL from the href attribute.

    Args:
        html_snippet: A string expected to contain an anchor tag, like
                      '<a href="some_url">...</a>'. Can be None.

    Returns:
        The extracted URL as a string if found, otherwise None.
    """
    if not html_snippet:
        logger.debug("Received empty or None HTML snippet.")
        return None

    url = None
    try:
        soup = BeautifulSoup(html_snippet, "html.parser")
        anchor_tag = soup.find("a")

        if anchor_tag:
            url = anchor_tag.get("href")  # type: ignore[attr-defined]
            if url:
                logger.debug("Extracted URL: %s", url)
            else:
                logger.warning("Found anchor tag but no 'href' in snippet: %s", html_snippet)
        else:
            logger.warning("No anchor tag found in snippet: %s", html_snippet)
    except Exception as e:
        logger.error("Error parsing HTML snippet'%s': %s", html_snippet, e, exc_info=True)

    return url


def _fetch_epw_header(epw_file_url: str) -> bytes | None:
    """Fetches the first part of an EnergyPlus Weather (EPW) file.

    Attempts to retrieve the initial bytes (typically the first 512) of the
    specified EPW file using an HTTP Range request. This is primarily used
    to access the header lines containing location metadata without downloading
    the entire file. Handles cases where the server might return the full file
    (status 200) instead of partial content (status 206).

    Args:
        epw_file_url: The direct URL to the .epw file.

    Returns:
        The raw byte content (partial or full) of the response body if the
        request is successful (status 2xx), otherwise None if a network,
        HTTP error, or other exception occurs.
    """
    try:
        headers = {"Range": "bytes=0-512"}
        response = requests.get(epw_file_url, headers=headers, timeout=15, stream=True)
        response.raise_for_status()

        if response.status_code not in [200, 206]:
            logger.warning("Unable to process response from %s with status code %d", epw_file_url, response.status_code)
            return None

        return response.content

    except requests.exceptions.RequestException as e:
        logger.error("Request failed for EPW URL %s: %s", epw_file_url, e)
        return None
    except Exception as e:
        logger.error("An unexpected error occurred processing EPW file from %s : %s", epw_file_url, e, exc_info=True)
        return None
