"""Functions for parsing HTML content and EnergyPlus weather file (EPW) data.

Provides utilities to extract relevant navigation and file links from HTML pages
retrieved from the weather site, and to parse the specific 'LOCATION' line
from the header of EPW files to extract metadata.
"""

import logging

from src.config import EPW_FIELD_NAMES

logger = logging.getLogger(__name__)

DECODING_SCHEMES = ["utf-8", "iso-8859-1"]


class MalformedLocationDataError(ValueError):
    """Error when receiving malformed epw header data."""

    def __init__(self) -> None:
        super().__init__("unable to parse epw location")


def extract_epw_location_line(epw_content: bytes, source_url: str) -> str | None:
    """Fetch the first line of an epw file.

    Args:
        epw_content: The first 512 bytes of an EPW file.
        source_url: The URL from which the epw_content was fetched (for logging).

    Returns:
        A string containing the first line of the EPW file, or None on error.
    """
    decoded_text = _try_decode_bytes(epw_content, source_url)

    if decoded_text is None:
        return None

    first_line = None  # only assigned if successful, otherwise will return None
    newline_pos = decoded_text.find("\n")

    if newline_pos != -1:
        first_line = decoded_text[:newline_pos].strip()
    else:
        logger.error("No newline found in epw_content for URL %s", source_url)

    return first_line


def _try_decode_bytes(content: bytes, url: str) -> str | None:
    """Attempts to decode bytes using a predefined list of encodings.

    Args:
        content: Bytes with unknown encoding.
        url: The URL from which the bytes were fetched (for logging).

    Returns:
        The decoded text if successful, or None on error.
    """
    for attempt, encoding in enumerate(DECODING_SCHEMES):
        try:
            decoded_text = content.decode(encoding)
            if attempt > 0:
                logger.warning("Successfully decoded using '%s' for %s", encoding, url)
            else:
                logger.debug("Successfully decoded using '%s' for %s", encoding, url)
        except UnicodeDecodeError:
            logger.debug("Decoding failed using '%s' for %s. Trying next...", encoding, url)
            continue
        except Exception:
            logger.exception("Unexpected error during %s decoding for url %s", encoding, url)
            return None
        else:
            return decoded_text

    # If the loop completes without returning, all attempts have failed.
    logger.error(
        "Failed to decode content using any attempted encoding (%s) for url %s", ", ".join(DECODING_SCHEMES), url
    )
    return None


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
        MalformedLocationDataError: If the epw location line format is unable to be parsed.
    """
    keys = EPW_FIELD_NAMES
    # Split the line by commas
    data = line.split(",")
    if data[0] != "LOCATION" or len(keys) != len(data) - 1:
        raise MalformedLocationDataError
    # Discard the first element ("LOCATION")
    data = data[1:]
    data[0] = data[0].title()
    if len(data[1]) < 2:
        data[1] = ""
    # Create a dictionary by zipping the predefined keys with the extracted data
    return dict(zip(keys, data, strict=False))
