"""Functions for parsing HTML content and EnergyPlus weather file (EPW) data.

Provides utilities to extract relevant navigation and file links from HTML pages
retrieved from the weather site, and to parse the specific 'LOCATION' line
from the header of EPW files to extract metadata.
"""

import logging

logger = logging.getLogger(__name__)


def extract_epw_location_line(epw_content: bytes, source_url: str) -> str | None:
    """Fetch the first line of an epw file.

    Args:
        epw_content: The first 1024 bytes of an EPW file, encoded as utf-8.
        source_url: The URL from which the epw_content was fetched (for logging).

    Returns:
        A string containing the first line of the EPW file, or None on error.
    """
    first_line = None  # only assigned if successful, otherwise will return None
    try:
        epw_text = epw_content.decode(encoding="utf-8")
        newline_pos = epw_text.find("\n")

        if newline_pos != -1:
            first_line = epw_text[:newline_pos].strip()
        else:
            logger.warning("No newline found in epw_content")
    except UnicodeDecodeError:
        logger.error("Unable to decode epw content (UTF-8) for URL: %s", source_url)
    except Exception as e:
        logger.error("Unable to process first line for URL %s : %s", source_url, e, exc_info=True)

    return first_line


def parse_epw_location_line(line: str) -> dict[str, str]:
    """Extracts location metadata from an EPW LOCATION line.

    Parses a comma-separated string conforming to the EPW file format's
    LOCATION line specification, skipping the initial "LOCATION" identifier.

    Args:
        line: The LOCATION line string from an EPW file.

    Returns:
        A dictionary mapping standard EPW location fields to their corresponding
        string values extracted from the line.

    Raises:
        ValueError: If the epw location line format is unable to be parsed.
    """
    keys = [
        "location",
        "region",
        "country",
        "weather_source",
        "wmo_index",
        "latitude",
        "longitude",
        "tz_offset",
        "elevation",
    ]
    # Split the line by commas
    data = line.split(",")
    if data[0] != "LOCATION" or len(keys) != len(data) - 1:
        raise ValueError("unable to parse epw location")
    # Discard the first element ("LOCATION")
    data = data[1:]
    data[0] = data[0].title()
    if len(data[1]) < 2:
        data[1] = ""
    # Create a dictionary by zipping the predefined keys with the extracted data
    return dict(zip(keys, data, strict=False))
